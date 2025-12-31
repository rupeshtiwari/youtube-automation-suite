"""
Flask web application for YouTube automation configuration and scheduling.
Provides a web interface to configure API keys and schedule daily automation.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
import json
import os
import sys
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database
from app import views

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Settings file - support NAS/Docker deployment
DATA_DIR = os.getenv('DATA_DIR', os.path.dirname(__file__))
SETTINGS_FILE = os.path.join(DATA_DIR, 'automation_settings.json')
SCHEDULER = BackgroundScheduler()
SCHEDULER.start()

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))


def load_settings():
    """Load settings from JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {
        'api_keys': {},
        'scheduling': {
            'enabled': False,
            'videos_per_day': 1,
            'youtube_schedule_time': '23:00',  # 11:00 PM IST
            'social_media_schedule_time': '19:30',  # 7:30 PM IST
            'schedule_day': 'wednesday',  # Day of week
            'playlist_id': '',
        'export_type': 'shorts',  # 'all' or 'shorts'
        'use_database': True,  # Use SQLite database instead of Excel
        'auto_post_social': False,
        'social_platforms': ['linkedin', 'facebook', 'instagram']
        },
        'last_run': None,
        'next_run': None
    }


def save_settings(settings):
    """Save settings to JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)
    
    # Also update .env file for compatibility
    update_env_file(settings)


def update_env_file(settings):
    """Update .env file with API keys."""
    env_lines = []
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    
    # Create mapping of keys
    api_keys = settings.get('api_keys', {})
    key_mapping = {
        'LINKEDIN_ACCESS_TOKEN': api_keys.get('linkedin_access_token', ''),
        'LINKEDIN_PERSON_URN': api_keys.get('linkedin_person_urn', ''),
        'FACEBOOK_PAGE_ACCESS_TOKEN': api_keys.get('facebook_page_access_token', ''),
        'FACEBOOK_PAGE_ID': api_keys.get('facebook_page_id', ''),
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': api_keys.get('instagram_business_account_id', ''),
        'INSTAGRAM_ACCESS_TOKEN': api_keys.get('instagram_access_token', ''),
        'AYRSHARE_API_KEY': api_keys.get('ayrshare_api_key', ''),
        'YOUTUBE_PLAYLIST_ID': settings.get('scheduling', {}).get('playlist_id', ''),
    }
    
    # Update or add keys
    existing_keys = set()
    new_lines = []
    for line in env_lines:
        if '=' in line and not line.strip().startswith('#'):
            key = line.split('=')[0].strip()
            if key in key_mapping:
                new_lines.append(f"{key}={key_mapping[key]}\n")
                existing_keys.add(key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    
    # Add missing keys
    for key, value in key_mapping.items():
        if key not in existing_keys and value:
            new_lines.append(f"{key}={value}\n")
    
    with open('.env', 'w') as f:
        f.writelines(new_lines)


def run_daily_automation():
    """Run the daily automation tasks."""
    settings = load_settings()
    scheduling = settings.get('scheduling', {})
    
    if not scheduling.get('enabled', False):
        print(f"[{datetime.now()}] Automation is disabled, skipping...")
        return
    
    print(f"[{datetime.now()}] Starting daily automation...")
    
    try:
        # Update .env file first to ensure scripts have access to API keys
        update_env_file(settings)
        
        # Step 1: Export videos
        export_type = scheduling.get('export_type', 'shorts')
        use_database = scheduling.get('use_database', True)
        
        if use_database:
            # Use database (recommended)
            if export_type == 'shorts':
                script = 'export_shorts_to_database.py'
            else:
                # For now, use Excel version for 'all' playlists
                # TODO: Create export_playlists_to_database.py
                script = 'export_playlists_videos_to_excel.py'
            
            result = subprocess.run(
                ['python', script],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=os.getcwd()
            )
        else:
            # Use Excel (legacy)
            if export_type == 'shorts':
                result = subprocess.run(
                    ['python', 'export_shorts_to_excel.py'],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=os.getcwd()
                )
            else:
                result = subprocess.run(
                    ['python', 'export_playlists_videos_to_excel.py'],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=os.getcwd()
                )
        
        if result.returncode != 0:
            print(f"Export failed: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return
        
        # Step 2: Schedule YouTube videos if playlist_id is set
        playlist_id = scheduling.get('playlist_id', '')
        videos_per_day = scheduling.get('videos_per_day', 1)
        
        if playlist_id:
            # Set environment variable
            env = os.environ.copy()
            env['YOUTUBE_PLAYLIST_ID'] = playlist_id
            
            # Run scheduling for specified number of videos
            # Note: schedule-youtube.py schedules ALL videos, so we might need to modify it
            # For now, we'll run it as-is
            result = subprocess.run(
                ['python', 'schedule-youtube.py'],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.getcwd()
            )
            
            if result.returncode != 0:
                print(f"YouTube scheduling failed: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")
        
        # Step 3: Post to social media if enabled
        if scheduling.get('auto_post_social', False):
            platforms = scheduling.get('social_platforms', [])
            
            if use_database:
                # Post from database (more efficient)
                from database import get_pending_posts
                from post_to_social_media import SocialMediaPoster
                
                poster = SocialMediaPoster(use_ayrshare=bool(settings.get('api_keys', {}).get('ayrshare_api_key')))
                
                for platform in platforms:
                    pending_posts = get_pending_posts(platform=platform.lower())
                    print(f"Found {len(pending_posts)} pending posts for {platform}")
                    
                    for post in pending_posts:
                        video_id = post['video_id']
                        content = post['post_content']
                        schedule_date = post['schedule_date']
                        
                        # Post to platform
                        if platform.lower() == 'linkedin':
                            result = poster.post_to_linkedin(content, schedule_date)
                        elif platform.lower() == 'facebook':
                            result = poster.post_to_facebook(content, schedule_date)
                        elif platform.lower() == 'instagram':
                            result = poster.post_to_instagram(content, None, schedule_date)
                        else:
                            continue
                        
                        # Update database
                        from database import update_post_status
                        if result.get('success'):
                            update_post_status(
                                video_id, platform.lower(), 
                                result.get('status', 'scheduled'),
                                result.get('scheduled_date'),
                                result.get('post_id')
                            )
                        else:
                            update_post_status(
                                video_id, platform.lower(), 'error',
                                error_message=result.get('error')
                            )
                        
                        time.sleep(2)  # Rate limiting
            else:
                # Post from Excel (legacy)
                excel_file = 'youtube_shorts_export.xlsx' if export_type == 'shorts' else 'youtube_playlists_videos_export.xlsx'
                
                if os.path.exists(excel_file):
                    use_ayrshare = bool(settings.get('api_keys', {}).get('ayrshare_api_key'))
                    cmd = [
                        'python', 'post_to_social_media.py',
                        '--excel', excel_file,
                        '--platforms'
                    ] + platforms
                    
                    if use_ayrshare:
                        cmd.append('--use-ayrshare')
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600,
                        cwd=os.getcwd()
                    )
                    
                    if result.returncode != 0:
                        print(f"Social media posting failed: {result.stderr}")
                        if result.stdout:
                            print(f"Output: {result.stdout}")
        
        # Update last run time
        settings['last_run'] = datetime.now(IST).isoformat()
        save_settings(settings)
        
        print(f"[{datetime.now()}] Daily automation completed successfully")
        
    except Exception as e:
        print(f"[{datetime.now()}] Error in daily automation: {e}")


def schedule_daily_job():
    """Schedule the daily automation job."""
    settings = load_settings()
    scheduling = settings.get('scheduling', {})
    
    # Remove existing jobs
    SCHEDULER.remove_all_jobs()
    
    if not scheduling.get('enabled', False):
        return
    
    # Parse schedule time
    schedule_time = scheduling.get('youtube_schedule_time', '23:00')
    hour, minute = map(int, schedule_time.split(':'))
    
    # Schedule day (convert to cron day)
    day_map = {
        'monday': 'mon',
        'tuesday': 'tue',
        'wednesday': 'wed',
        'thursday': 'thu',
        'friday': 'fri',
        'saturday': 'sat',
        'sunday': 'sun'
    }
    day = day_map.get(scheduling.get('schedule_day', 'wednesday').lower(), 'wed')
    
    # Schedule job (IST timezone)
    SCHEDULER.add_job(
        func=run_daily_automation,
        trigger=CronTrigger(
            day_of_week=day,
            hour=hour,
            minute=minute,
            timezone=IST
        ),
        id='daily_automation',
        name='Daily YouTube Automation',
        replace_existing=True
    )
    
    # Calculate next run
    now = datetime.now(IST)
    next_run = SCHEDULER.get_job('daily_automation').next_run_time
    settings['next_run'] = next_run.isoformat() if next_run else None
    save_settings(settings)


@app.route('/')
def index():
    """Dashboard home page."""
    settings = load_settings()
    return render_template('dashboard.html', settings=settings)


@app.route('/docs')
@app.route('/documentation')
def documentation():
    """Documentation page."""
    return render_template('documentation.html')


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    from database import DB_PATH
    return jsonify({
        'status': 'healthy',
        'database_exists': os.path.exists(DB_PATH),
        'timestamp': datetime.now(IST).isoformat()
    })


@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page."""
    if request.method == 'POST':
        settings = load_settings()
        
        # Update API keys
        settings['api_keys'] = {
            'linkedin_access_token': request.form.get('linkedin_access_token', ''),
            'linkedin_person_urn': request.form.get('linkedin_person_urn', ''),
            'facebook_page_access_token': request.form.get('facebook_page_access_token', ''),
            'facebook_page_id': request.form.get('facebook_page_id', ''),
            'instagram_business_account_id': request.form.get('instagram_business_account_id', ''),
            'instagram_access_token': request.form.get('instagram_access_token', ''),
            'ayrshare_api_key': request.form.get('ayrshare_api_key', ''),
        }
        
        # Update scheduling settings
        settings['scheduling'] = {
            'enabled': request.form.get('scheduling_enabled') == 'on',
            'videos_per_day': int(request.form.get('videos_per_day', 1)),
            'youtube_schedule_time': request.form.get('youtube_schedule_time', '23:00'),
            'social_media_schedule_time': request.form.get('social_media_schedule_time', '19:30'),
            'schedule_day': request.form.get('schedule_day', 'wednesday'),
            'playlist_id': request.form.get('playlist_id', ''),
            'export_type': request.form.get('export_type', 'shorts'),
            'use_database': request.form.get('use_database') == 'on',
            'auto_post_social': request.form.get('auto_post_social') == 'on',
            'social_platforms': request.form.getlist('social_platforms'),
        }
        
        save_settings(settings)
        schedule_daily_job()
        
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('config'))
    
    settings = load_settings()
    return render_template('config.html', settings=settings)


@app.route('/api/status')
def api_status():
    """API endpoint for automation status."""
    settings = load_settings()
    job = SCHEDULER.get_job('daily_automation')
    
    return jsonify({
        'enabled': settings.get('scheduling', {}).get('enabled', False),
        'last_run': settings.get('last_run'),
        'next_run': settings.get('next_run'),
        'job_running': job is not None,
        'job_next_run': job.next_run_time.isoformat() if job and job.next_run_time else None
    })


@app.route('/api/run-now', methods=['POST'])
def run_now():
    """Manually trigger automation now."""
    thread = threading.Thread(target=run_daily_automation)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'message': 'Automation started in background'})


def get_my_channel_id_helper(youtube):
    """Helper to get channel ID."""
    try:
        resp = youtube.channels().list(part="id", mine=True).execute()
        items = resp.get("items", [])
        if not items:
            return None
        return items[0]["id"]
    except:
        return None


def get_youtube_service():
    """Get YouTube API service."""
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
        CLIENT_SECRET_FILE = "client_secret.json"
        TOKEN_FILE = "token.json"
        
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        print(f"Error getting YouTube service: {e}")
        return None


def fetch_all_playlists_from_youtube(youtube, channel_id: str):
    """Fetch all playlists from YouTube."""
    playlists = []
    page_token = None
    
    while True:
        try:
            if page_token:
                response = youtube.playlists().list(
                    part="id,snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=page_token
                ).execute()
            else:
                response = youtube.playlists().list(
                    part="id,snippet,contentDetails",
                    channelId=channel_id,
                    maxResults=50
                ).execute()
            
            for pl in response.get("items", []):
                snippet = pl.get("snippet", {})
                playlists.append({
                    "playlistId": pl["id"],
                    "playlistTitle": snippet.get("title", ""),
                    "playlistDescription": snippet.get("description", ""),
                    "playlistUrl": f"https://www.youtube.com/playlist?list={pl['id']}",
                    "itemCount": pl.get("contentDetails", {}).get("itemCount", 0),
                    "publishedAt": snippet.get("publishedAt", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("default", {}).get("url", "")
                })
            
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            break
    
    return playlists


def fetch_playlist_videos_from_youtube(youtube, playlist_id: str, channel_title: str = ""):
    """Fetch all videos in a playlist from YouTube."""
    videos = []
    page_token = None
    
    while True:
        try:
            if page_token:
                response = youtube.playlistItems().list(
                    part="id,snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=50,
                    pageToken=page_token
                ).execute()
            else:
                response = youtube.playlistItems().list(
                    part="id,snippet,contentDetails",
                    playlistId=playlist_id,
                    maxResults=50
                ).execute()
            
            video_ids = [item["contentDetails"]["videoId"] for item in response.get("items", [])]
            
            if video_ids:
                # Get video details in batches
                for i in range(0, len(video_ids), 50):
                    batch = video_ids[i:i+50]
                    videos_response = youtube.videos().list(
                        part="id,snippet,status",
                        id=",".join(batch),
                        maxResults=50
                    ).execute()
                    
                    for video in videos_response.get("items", []):
                        snippet = video.get("snippet", {})
                        status = video.get("status", {})
                        video_id = video["id"]
                        
                        # Get channel title from snippet
                        channel_name = snippet.get("channelTitle", channel_title)
                        
                        # Determine publish date vs schedule date
                        published_at = snippet.get("publishedAt", "")
                        publish_at = status.get("publishAt", "")
                        privacy_status = status.get("privacyStatus", "")
                        
                        # Determine if scheduled (future date) or published
                        from datetime import datetime
                        is_scheduled = False
                        display_date = published_at
                        date_label = "Published"
                        
                        if publish_at:
                            try:
                                pub_date = datetime.fromisoformat(publish_at.replace('Z', '+00:00'))
                                # If publishAt is in the future, it's scheduled
                                if pub_date > datetime.now(pub_date.tzinfo):
                                    is_scheduled = True
                                    display_date = publish_at
                                    date_label = "Scheduled"
                            except:
                                pass
                        
                        if privacy_status == "private" and publish_at:
                            is_scheduled = True
                            display_date = publish_at
                            date_label = "Scheduled"
                        elif privacy_status == "public":
                            date_label = "Published"
                            display_date = published_at
                        
                        videos.append({
                            "videoId": video_id,
                            "title": snippet.get("title", ""),
                            "description": snippet.get("description", ""),
                            "thumbnail": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                            "publishedAt": published_at,
                            "publishAt": publish_at,
                            "privacyStatus": privacy_status,
                            "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
                            "tags": ", ".join(snippet.get("tags", [])),
                            "channelTitle": channel_name,
                            "displayDate": display_date,
                            "dateLabel": date_label,
                            "isScheduled": is_scheduled
                        })
            
            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Error fetching playlist videos: {e}")
            import traceback
            traceback.print_exc()
            break
    
    return videos


def get_video_social_posts_from_db(video_id: str):
    """Get social media posts for a video from database."""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    posts = {}
    for platform in ['linkedin', 'facebook', 'instagram']:
        cursor.execute('''
            SELECT post_content, schedule_date, actual_scheduled_date, status
            FROM social_media_posts
            WHERE video_id = ? AND platform = ?
        ''', (video_id, platform))
        
        row = cursor.fetchone()
        if row:
            posts[platform] = {
                'post_content': row[0],
                'schedule_date': row[1],
                'actual_scheduled_date': row[2],
                'status': row[3]
            }
        else:
            posts[platform] = None
    
    conn.close()
    return posts


@app.route('/playlists')
def playlists():
    """Display all playlists and videos - always fetches fresh data from YouTube."""
    youtube = get_youtube_service()
    if not youtube:
        return render_template('error.html', 
                             message="YouTube API not configured. Please set up client_secret.json")
    
    try:
        # Always fetch fresh data from YouTube API (no caching)
        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return render_template('error.html', 
                                 message="Could not find your YouTube channel. Please check authentication.")
        
        # Fetch latest playlists from YouTube API
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)
        channel_title = playlists_data[0].get("channelTitle", "") if playlists_data else ""
        
        # Videos will be loaded on demand via AJAX (also fetches fresh from YouTube)
        for playlist in playlists_data:
            playlist["videos"] = []
            playlist["videosLoaded"] = False
        
        # Add cache control headers to prevent browser caching
        response = make_response(render_template('playlists.html', playlists=playlists_data, channel_title=channel_title))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        return render_template('error.html', message=f"Error fetching playlists: {str(e)}\n{traceback.format_exc()}")


@app.route('/api/playlist/<playlist_id>/videos')
def api_playlist_videos(playlist_id):
    """API endpoint to fetch videos for a playlist (lazy loading)."""
    youtube = get_youtube_service()
    if not youtube:
        return jsonify({'error': 'YouTube API not configured'}), 500
    
    try:
        # Get channel info for channel title
        channel_id = get_my_channel_id_helper(youtube)
        channel_title = ""
        if channel_id:
            try:
                channel_response = youtube.channels().list(part="snippet", id=channel_id).execute()
                if channel_response.get("items"):
                    channel_title = channel_response["items"][0].get("snippet", {}).get("title", "")
            except:
                pass
        
        videos = fetch_playlist_videos_from_youtube(youtube, playlist_id, channel_title)
        
        # Add social media posts and tags from database
        from tagging import derive_type_enhanced, derive_role_enhanced, suggest_tags
        from database import get_video
        
        for video in videos:
            video_id = video["videoId"]
            social_posts = get_video_social_posts_from_db(video_id)
            video["social_posts"] = social_posts
            
            # Get video from database for tags
            db_video = get_video(video_id)
            if db_video:
                video["video_type"] = db_video.get("video_type", "")
                video["role"] = db_video.get("role", "")
                video["custom_tags"] = db_video.get("custom_tags", "")
            else:
                # Auto-derive type and role if not in DB
                playlist_title = ""  # We don't have playlist title here, but can get from context
                video_type = derive_type_enhanced(
                    playlist_title,
                    video.get("title", ""),
                    video.get("description", ""),
                    video.get("tags", "")
                )
                role = derive_role_enhanced(
                    playlist_title,
                    video.get("title", ""),
                    video.get("description", ""),
                    video.get("tags", "")
                )
                video["video_type"] = video_type
                video["role"] = role
                video["custom_tags"] = ""
                
                # Suggest tags
                suggested_tags = suggest_tags(
                    video.get("title", ""),
                    video.get("description", ""),
                    video_type,
                    role
                )
                video["suggested_tags"] = suggested_tags
        
        # Add cache control headers to prevent browser caching
        response = make_response(jsonify({'videos': videos}))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/video/<video_id>/tags', methods=['GET', 'POST'])
def api_video_tags(video_id):
    """Get or update video tags."""
    from database import get_video, get_db_connection
    from tagging import parse_tags, format_tags
    
    if request.method == 'GET':
        video = get_video(video_id)
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        return jsonify({
            'video_type': video.get('video_type', ''),
            'role': video.get('role', ''),
            'custom_tags': video.get('custom_tags', ''),
            'tags': parse_tags(video.get('custom_tags', ''))
        })
    
    elif request.method == 'POST':
        data = request.json
        video_type = data.get('video_type', '')
        role = data.get('role', '')
        custom_tags = format_tags(data.get('tags', []))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE videos 
            SET video_type = ?, role = ?, custom_tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE video_id = ?
        ''', (video_type, role, custom_tags, video_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Tags updated successfully'})


@app.route('/api/videos/search')
def api_search_videos():
    """Search videos by query, type, role, or tags."""
    from database import get_db_connection
    from tagging import search_videos, parse_tags
    
    query = request.args.get('q', '')
    video_type = request.args.get('type', '')
    role = request.args.get('role', '')
    tags_param = request.args.get('tags', '')
    
    tags = parse_tags(tags_param) if tags_param else None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build query
    sql = "SELECT * FROM videos "
    where_clause = search_videos(query, video_type if video_type else None, 
                                role if role else None, tags)
    sql += where_clause
    sql += " ORDER BY updated_at DESC LIMIT 100"
    
    # Build parameters
    params = []
    if query:
        query_param = f"%{query}%"
        params.extend([query_param, query_param, query_param, query_param])
    if video_type:
        params.append(video_type)
    if role:
        params.append(role)
    if tags:
        for tag in tags:
            tag_param = f"%{tag}%"
            params.extend([tag_param, tag_param])
    
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    
    videos = [dict(row) for row in rows]
    return jsonify({'videos': videos, 'count': len(videos)})


@app.route('/calendar')
def calendar():
    """Display calendar view of scheduled posts."""
    return render_template('calendar.html')


@app.route('/api/calendar-data')
def api_calendar_data():
    """API endpoint for calendar data (JSON)."""
    from app.database import get_videos_for_export
    import pandas as pd
    
    try:
        df = get_videos_for_export()
        calendar_events = []
        
        for _, row in df.iterrows():
            video_id = row.get('Video Name', '')
            title = row.get('Title', '')
            youtube_url = row.get('YouTube URL', '')
            video_type = row.get('Type', '') or ''
            role = row.get('Role', '') or ''
            custom_tags = row.get('Custom Tags', '') or ''
            playlist_name = row.get('Playlist Name', '') or ''
            description = row.get('Description', '') or ''
            
            for platform in ['LinkedIn', 'Facebook', 'Instagram']:
                schedule_col = f'{platform} Schedule Date'
                actual_col = f'{platform} Actual Scheduled Date'
                status_col = f'{platform} Status'
                post_col = f'{platform} Post'
                
                date = row.get(schedule_col) or row.get(actual_col)
                if pd.notna(date) and date:
                    try:
                        dt = pd.to_datetime(date)
                        calendar_events.append({
                            'date': dt.strftime('%Y-%m-%d'),
                            'time': dt.strftime('%H:%M:%S') if len(str(dt.time())) > 5 else dt.strftime('%H:%M') + ':00',
                            'datetime': dt.isoformat(),
                            'platform': platform,
                            'video_title': title,
                            'video_id': video_id,
                            'youtube_url': youtube_url,
                            'status': row.get(status_col, 'pending'),
                            'post_content': row.get(post_col, ''),
                            'video_type': video_type,
                            'role': role,
                            'custom_tags': custom_tags,
                            'playlist_name': playlist_name,
                            'description': description[:200] + '...' if description and len(description) > 200 else description
                        })
                    except:
                        pass
        
        calendar_events.sort(key=lambda x: x['datetime'])
        return jsonify({'events': calendar_events})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc(), 'events': []}), 500


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test API connection."""
    platform = request.json.get('platform')
    settings = load_settings()
    api_keys = settings.get('api_keys', {})
    
    # Simple validation - check if key exists
    if platform == 'linkedin':
        has_token = bool(api_keys.get('linkedin_access_token'))
        has_urn = bool(api_keys.get('linkedin_person_urn'))
        return jsonify({
            'success': has_token and has_urn,
            'message': 'LinkedIn configured' if (has_token and has_urn) else 'Missing LinkedIn credentials'
        })
    elif platform == 'facebook':
        has_token = bool(api_keys.get('facebook_page_access_token'))
        has_id = bool(api_keys.get('facebook_page_id'))
        return jsonify({
            'success': has_token and has_id,
            'message': 'Facebook configured' if (has_token and has_id) else 'Missing Facebook credentials'
        })
    elif platform == 'instagram':
        has_account = bool(api_keys.get('instagram_business_account_id'))
        has_token = bool(api_keys.get('instagram_access_token'))
        return jsonify({
            'success': has_account and has_token,
            'message': 'Instagram configured' if (has_account and has_token) else 'Missing Instagram credentials'
        })
    elif platform == 'ayrshare':
        has_key = bool(api_keys.get('ayrshare_api_key'))
        return jsonify({
            'success': has_key,
            'message': 'Ayrshare configured' if has_key else 'Missing Ayrshare API key'
        })
    
    return jsonify({'success': False, 'message': 'Unknown platform'})


# Shutdown scheduler on app exit
atexit.register(lambda: SCHEDULER.shutdown())

if __name__ == '__main__':
    # Load initial settings and schedule job
    schedule_daily_job()
    
    # Run Flask app
    # Use environment variable for port, default to 5001 (5000 often used by AirPlay on macOS)
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print(f"\n🌐 Starting server on port {port}...")
    print(f"📱 Open in browser: http://localhost:{port}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

