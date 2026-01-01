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

# Get project root (parent of app/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(project_root, 'templates')

app = Flask(__name__, template_folder=template_dir)
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
        'api_keys': {
            'linkedin_client_id': '',
            'linkedin_client_secret': '',
            'linkedin_access_token': '',
            'linkedin_person_urn': '',
            'facebook_app_id': '',
            'facebook_app_secret': '',
            'facebook_page_access_token': '',
            'facebook_page_id': '',
            'instagram_business_account_id': '',
            'instagram_access_token': '',
        },
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
        'thresholds': {
            'linkedin_daily_limit': 25,  # LinkedIn allows ~25 posts/day
            'facebook_daily_limit': 25,  # Facebook allows ~25 posts/day
            'instagram_daily_limit': 25,  # Instagram allows ~25 posts/day
            'youtube_daily_limit': 10  # YouTube allows ~10 videos/day
        },
        'targeting': {
            'target_audience': 'usa_students',  # 'usa_students', 'all', 'professionals'
            'interview_types': ['coding_interview', 'sys_design_interview', 'leetcode', 'algorithm_interview', 'behavioral_interview'],
            'role_levels': ['intern', 'new_grad', 'entry_level', 'student'],  # Target student roles
            'timezone': 'America/New_York',  # USA Eastern Time
            'optimal_times': ['14:00', '17:00', '21:00']  # 2 PM, 5 PM, 9 PM EDT (USA student active times)
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
        'LINKEDIN_CLIENT_ID': api_keys.get('linkedin_client_id', ''),
        'LINKEDIN_CLIENT_SECRET': api_keys.get('linkedin_client_secret', ''),
        'LINKEDIN_ACCESS_TOKEN': api_keys.get('linkedin_access_token', ''),
        'LINKEDIN_PERSON_URN': api_keys.get('linkedin_person_urn', ''),
        'FACEBOOK_APP_ID': api_keys.get('facebook_app_id', ''),
        'FACEBOOK_APP_SECRET': api_keys.get('facebook_app_secret', ''),
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
                from app.database import get_pending_posts
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
                        from app.database import update_post_status
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
    from app.database import DB_PATH
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
            'linkedin_client_id': request.form.get('linkedin_client_id', ''),
            'linkedin_client_secret': request.form.get('linkedin_client_secret', ''),
            'linkedin_access_token': request.form.get('linkedin_access_token', ''),
            'linkedin_person_urn': request.form.get('linkedin_person_urn', ''),
            'facebook_app_id': request.form.get('facebook_app_id', ''),
            'facebook_app_secret': request.form.get('facebook_app_secret', ''),
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
        
        # Update thresholds
        settings['thresholds'] = {
            'linkedin_daily_limit': int(request.form.get('linkedin_daily_limit', 25)),
            'facebook_daily_limit': int(request.form.get('facebook_daily_limit', 25)),
            'instagram_daily_limit': int(request.form.get('instagram_daily_limit', 25)),
            'youtube_daily_limit': int(request.form.get('youtube_daily_limit', 10)),
        }
        
        # Update targeting
        settings['targeting'] = {
            'target_audience': request.form.get('target_audience', 'usa_students'),
            'interview_types': request.form.getlist('interview_types'),
            'role_levels': request.form.getlist('role_levels'),
            'timezone': 'America/New_York',  # USA Eastern Time
            'optimal_times': ['14:00', '17:00', '21:00']  # 2 PM, 5 PM, 9 PM EDT
        }
        
        save_settings(settings)
        schedule_daily_job()
        
        flash('Settings saved successfully!', 'success')
        return redirect(url_for('config'))
    
    settings = load_settings()
    
    # Check YouTube API status
    youtube_status = {
        'configured': False,
        'client_secret_exists': False,
        'channel_name': None,
        'channel_id': None,
        'error': None
    }
    
    try:
        client_secret_path = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')
        client_secret_path = os.path.abspath(client_secret_path)
        youtube_status['client_secret_exists'] = os.path.exists(client_secret_path)
        
        if youtube_status['client_secret_exists']:
            # Try to get YouTube service to verify connection
            try:
                youtube = views.get_youtube_service()
                if youtube:
                    channel_id = get_my_channel_id_helper(youtube)
                    if channel_id:
                        youtube_status['channel_id'] = channel_id
                        youtube_status['configured'] = True
                        # Get channel name
                        try:
                            channel_response = youtube.channels().list(part="snippet", id=channel_id).execute()
                            if channel_response.get("items"):
                                youtube_status['channel_name'] = channel_response["items"][0].get("snippet", {}).get("title", "")
                        except:
                            pass
            except Exception as e:
                youtube_status['error'] = str(e)
    except Exception as e:
        youtube_status['error'] = str(e)
    
    return render_template('config.html', settings=settings, youtube_status=youtube_status)


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
    from app.database import get_db_connection
    
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
                'platform': platform,
                'post_content': row[0],
                'schedule_date': row[1],
                'actual_scheduled_date': row[2],
                'status': row[3]
            }
        else:
            posts[platform] = None
    
    conn.close()
    # Return as list for compatibility
    return [posts[platform] for platform in ['linkedin', 'facebook', 'instagram'] if posts.get(platform)]


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


@app.route('/shorts')
def shorts():
    """Display only Shorts playlists for weekly scheduling automation."""
    youtube = get_youtube_service()
    if not youtube:
        return render_template('error.html', 
                             message="YouTube API not configured. Please set up client_secret.json")
    
    try:
        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return render_template('error.html', 
                                 message="Could not find your YouTube channel. Please check authentication.")
        
        # Fetch all playlists and filter for Shorts
        all_playlists = fetch_all_playlists_from_youtube(youtube, channel_id)
        
        # Filter for Shorts playlists (case-insensitive check for "short" in title)
        shorts_playlists = [
            pl for pl in all_playlists 
            if 'short' in pl.get('playlistTitle', '').lower()
        ]
        
        # Initialize videos as empty (will be loaded on demand)
        for playlist in shorts_playlists:
            playlist["videos"] = []
            playlist["videosLoaded"] = False
        
        # Get settings for weekly schedule info
        settings = load_settings()
        weekly_schedule = settings.get('scheduling', {}).get('youtube_schedule_time', '23:00')
        schedule_day = settings.get('scheduling', {}).get('schedule_day', 'wednesday')
        
        response = make_response(render_template(
            'shorts.html', 
            playlists=shorts_playlists,
            weekly_schedule=weekly_schedule,
            schedule_day=schedule_day
        ))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    except Exception as e:
        import traceback
        return render_template('error.html', message=f"Error fetching Shorts: {str(e)}\n{traceback.format_exc()}")


@app.route('/insights')
def insights():
    """Rich insights dashboard showing analytics from all platforms."""
    try:
        # Get YouTube Analytics if available
        youtube_analytics = get_youtube_analytics()
        
        # Get Facebook Insights if available
        facebook_insights = get_facebook_insights()
        
        # Get LinkedIn Analytics if available
        linkedin_analytics = get_linkedin_analytics()
        
        # Combine all insights
        insights_data = {
            'youtube': youtube_analytics,
            'facebook': facebook_insights,
            'linkedin': linkedin_analytics,
            'optimal_posting_times': calculate_optimal_posting_times(youtube_analytics, facebook_insights, linkedin_analytics)
        }
        
        return render_template('insights.html', insights=insights_data)
    except Exception as e:
        import traceback
        return render_template('error.html', message=f"Error loading insights: {str(e)}\n{traceback.format_exc()}")


def get_youtube_analytics():
    """Get YouTube Analytics data."""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return {'error': 'YouTube API not configured'}
        
        # Need YouTube Analytics API (different from Data API)
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        import os
        
        SCOPES_ANALYTICS = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
        TOKEN_FILE = "token.json"
        
        creds = None
        if os.path.exists(TOKEN_FILE):
            from google.oauth2.credentials import Credentials
            # Try to load with analytics scope
            try:
                creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES_ANALYTICS)
            except:
                # If token doesn't have analytics scope, return error
                return {'error': 'YouTube Analytics API not authenticated. Please re-authenticate with analytics scope.'}
        
        if not creds or not creds.valid:
            return {'error': 'YouTube Analytics not authenticated'}
        
        analytics = build('youtubeAnalytics', 'v2', credentials=creds)
        channel_id = get_my_channel_id_helper(youtube)
        
        if not channel_id:
            return {'error': 'Channel ID not found'}
        
        # Get views, watch time, subscribers
        end_date = datetime.now(IST).strftime('%Y-%m-%d')
        start_date = (datetime.now(IST) - timedelta(days=30)).strftime('%Y-%m-%d')
        
        try:
            # Views and watch time
            views_response = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched,subscribersGained',
                dimensions='day'
            ).execute()
            
            # Demographics - Geography
            geo_response = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views',
                dimensions='country'
            ).execute()
            
            # Demographics - Age and Gender
            demo_response = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views',
                dimensions='ageGroup,gender'
            ).execute()
            
            # Audience activity by hour
            hourly_response = analytics.reports().query(
                ids=f'channel=={channel_id}',
                startDate=start_date,
                endDate=end_date,
                metrics='views',
                dimensions='day,hour'
            ).execute()
            
            return {
                'views_data': views_response.get('rows', []),
                'geography': geo_response.get('rows', []),
                'demographics': demo_response.get('rows', []),
                'hourly_activity': hourly_response.get('rows', []),
                'channel_id': channel_id
            }
        except Exception as e:
            return {'error': f'YouTube Analytics API error: {str(e)}', 'note': 'YouTube Analytics API may need to be enabled in Google Cloud Console'}
    except Exception as e:
        return {'error': f'Error getting YouTube Analytics: {str(e)}'}


def get_facebook_insights():
    """Get Facebook Page Insights."""
    try:
        settings = load_settings()
        api_keys = settings.get('api_keys', {})
        page_id = api_keys.get('facebook_page_id', '')
        access_token = api_keys.get('facebook_page_access_token', '')
        
        if not page_id or not access_token:
            return {'error': 'Facebook credentials not configured'}
        
        import requests
        
        # Get page insights
        url = f'https://graph.facebook.com/v18.0/{page_id}/insights'
        params = {
            'metric': 'page_impressions,page_reach,page_engaged_users,page_fans',
            'period': 'day',
            'since': int((datetime.now(IST) - timedelta(days=30)).timestamp()),
            'until': int(datetime.now(IST).timestamp()),
            'access_token': access_token
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return {'insights': data.get('data', [])}
        else:
            return {'error': f'Facebook API error: {response.text}'}
    except Exception as e:
        return {'error': f'Error getting Facebook Insights: {str(e)}'}


def get_linkedin_analytics():
    """Get LinkedIn Analytics data."""
    try:
        settings = load_settings()
        api_keys = settings.get('api_keys', {})
        access_token = api_keys.get('linkedin_access_token', '')
        
        if not access_token:
            return {'error': 'LinkedIn credentials not configured'}
        
        import requests
        
        # LinkedIn Analytics API endpoint
        url = 'https://api.linkedin.com/v2/analytics'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Note: LinkedIn Analytics API requires specific permissions
        # This is a placeholder - actual implementation depends on LinkedIn API version
        return {'note': 'LinkedIn Analytics requires specific API access', 'error': 'Not fully implemented'}
    except Exception as e:
        return {'error': f'Error getting LinkedIn Analytics: {str(e)}'}


def calculate_optimal_posting_times(youtube_data, facebook_data, linkedin_data):
    """Calculate optimal posting times based on audience activity."""
    optimal_times = {
        'youtube': None,
        'facebook': None,
        'linkedin': None,
        'overall': None
    }
    
    try:
        # Analyze YouTube hourly activity
        if youtube_data and 'hourly_activity' in youtube_data and youtube_data.get('hourly_activity'):
            hourly_views = {}
            for row in youtube_data['hourly_activity']:
                hour = row[1] if len(row) > 1 else 0
                views = row[2] if len(row) > 2 else 0
                hourly_views[hour] = hourly_views.get(hour, 0) + views
            
            if hourly_views:
                best_hour = max(hourly_views.items(), key=lambda x: x[1])[0]
                optimal_times['youtube'] = {
                    'hour': best_hour,
                    'best_times': sorted(hourly_views.items(), key=lambda x: x[1], reverse=True)[:3]
                }
        
        # Analyze Facebook insights for best posting times
        if facebook_data and 'insights' in facebook_data:
            # Facebook provides insights data - would need to parse for time patterns
            optimal_times['facebook'] = {'note': 'Analyze Facebook insights data for time patterns'}
        
        # Overall recommendation
        if optimal_times['youtube']:
            optimal_times['overall'] = optimal_times['youtube']
        
        return optimal_times
    except Exception as e:
        return {'error': f'Error calculating optimal times: {str(e)}'}


@app.route('/activity')
def activity():
    """Activity log page showing all automation activities."""
    from app.database import get_activity_logs
    
    # Get activity logs (last 200 by default)
    logs = get_activity_logs(limit=200)
    
    return render_template('activity.html', logs=logs)


@app.route('/api/autopilot/run', methods=['POST'])
def api_autopilot_run():
    """Run auto-pilot mode: select one video from each playlist and schedule on all channels."""
    try:
        from app.database import (
            log_activity, get_scheduled_count_today,
            insert_or_update_social_post, get_video, get_video_social_posts_from_db
        )
        
        settings = load_settings()
        thresholds = settings.get('thresholds', {})
        platforms = settings.get('scheduling', {}).get('social_platforms', ['linkedin', 'facebook', 'instagram'])
        
        youtube = get_youtube_service()
        if not youtube:
            return jsonify({'error': 'YouTube API not configured'}), 400
        
        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return jsonify({'error': 'Could not find YouTube channel'}), 400
        
        # Get all playlists
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)
        
        # Filter to Shorts playlists only (you can change this filter)
        shorts_playlists = [pl for pl in playlists_data if "short" in pl.get("playlistTitle", "").lower()]
        
        if not shorts_playlists:
            return jsonify({'error': 'No playlists found'}), 400
        
        selected_videos = []
        activities = []
        today_str = datetime.now(IST).strftime('%Y-%m-%d')
        
        # Get targeting settings
        targeting = settings.get('targeting', {})
        target_audience = targeting.get('target_audience', 'all')
        interview_types = targeting.get('interview_types', [])
        role_levels = targeting.get('role_levels', [])
        
        # Import tagging functions for filtering
        from app.tagging import derive_type_enhanced, derive_role_enhanced
        from app.database import get_video
        
        # Select one video from each playlist (with targeting filter)
        for playlist in shorts_playlists:
            playlist_id = playlist['playlistId']
            videos = fetch_playlist_videos_from_youtube(youtube, playlist_id, playlist.get('channelTitle', ''))
            
            if videos:
                selected_video = None
                playlist_title = playlist.get('playlistTitle', '')
                
                # Filter videos based on targeting criteria
                for video in videos:
                    video_id = video['videoId']
                    
                    # Get video from database or derive type/role
                    db_video = get_video(video_id)
                    if db_video:
                        video_type = db_video.get('video_type', '')
                        role = db_video.get('role', '')
                    else:
                        # Derive type and role from content
                        video_type = derive_type_enhanced(
                            playlist_title,
                            video.get('title', ''),
                            video.get('description', ''),
                            video.get('tags', '')
                        )
                        role = derive_role_enhanced(
                            playlist_title,
                            video.get('title', ''),
                            video.get('description', ''),
                            video.get('tags', '')
                        )
                    
                    # Apply targeting filters if targeting USA students
                    if target_audience == 'usa_students':
                        # Check if video type matches interview types
                        type_matches = not interview_types or any(
                            it in video_type for it in interview_types
                        )
                        
                        # Check if role matches student roles
                        role_matches = not role_levels or any(
                            rl in role for rl in role_levels
                        ) or role == ''  # Allow videos without specific role
                        
                        if type_matches or role_matches:
                            selected_video = video
                            break
                    else:
                        # No targeting - select first video
                        selected_video = video
                        break
                
                # If no video matched filters, select first one
                if not selected_video and videos:
                    selected_video = videos[0]
                
                if selected_video:
                    video_id = selected_video['videoId']
                    selected_videos.append({
                        'video': selected_video,
                        'playlist_id': playlist_id,
                        'playlist_name': playlist.get('playlistTitle', '')
                    })
        
        # Schedule selected videos to all platforms (respecting thresholds)
        scheduled_count = 0
        for item in selected_videos:
            video = item['video']
            video_id = video['videoId']
            video_title = video.get('title', '')
            playlist_id = item['playlist_id']
            playlist_name = item['playlist_name']
            
            # Get existing social posts or generate new ones
            existing_posts = get_video_social_posts_from_db(video_id)
            
            # Get or generate social media posts
            for platform in platforms:
                # Check threshold
                platform_limit_key = f'{platform}_daily_limit'
                daily_limit = thresholds.get(platform_limit_key, 25)
                scheduled_today = get_scheduled_count_today(platform, today_str)
                
                if scheduled_today >= daily_limit:
                    log_activity(
                        'schedule_post',
                        platform=platform,
                        video_id=video_id,
                        video_title=video_title,
                        playlist_id=playlist_id,
                        playlist_name=playlist_name,
                        status='skipped',
                        message=f'Daily limit reached ({scheduled_today}/{daily_limit})'
                    )
                    activities.append({
                        'action': 'skipped',
                        'platform': platform,
                        'video_title': video_title,
                        'reason': f'Daily limit reached'
                    })
                    continue
                
                # Get existing post content or use placeholder
                post_content = None
                for post in existing_posts:
                    if post.get('platform') == platform:
                        post_content = post.get('post_content', '')
                        break
                
                if not post_content:
                    # Generate simple post content
                    db_video = get_video(video_id)
                    title = db_video.get('title', video_title) if db_video else video_title
                    description = db_video.get('description', video.get('description', '')) if db_video else video.get('description', '')
                    youtube_url = f"https://youtube.com/watch?v={video_id}"
                    post_content = f"{title}\n\n{youtube_url}"
                
                # Calculate schedule date (next scheduled day/time)
                schedule_time = settings.get('scheduling', {}).get('social_media_schedule_time', '19:30')
                schedule_day = settings.get('scheduling', {}).get('schedule_day', 'wednesday')
                
                # Calculate next occurrence
                today = datetime.now(IST)
                days_ahead = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 
                             'friday': 4, 'saturday': 5, 'sunday': 6}[schedule_day.lower()]
                next_date = today + timedelta(days=(days_ahead - today.weekday()) % 7)
                if next_date <= today:
                    next_date += timedelta(days=7)
                
                schedule_datetime = f"{next_date.strftime('%Y-%m-%d')} {schedule_time}"
                
                # Save to database
                insert_or_update_social_post(video_id, platform, {
                    'post_content': post_content,
                    'schedule_date': schedule_datetime,
                    'status': 'pending'
                })
                
                log_activity(
                    'schedule_post',
                    platform=platform,
                    video_id=video_id,
                    video_title=video_title,
                    playlist_id=playlist_id,
                    playlist_name=playlist_name,
                    status='success',
                    message=f'Scheduled for {schedule_datetime}',
                    details={'schedule_date': schedule_datetime}
                )
                
                activities.append({
                    'action': 'scheduled',
                    'platform': platform,
                    'video_title': video_title,
                    'schedule_date': schedule_datetime
                })
                scheduled_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Auto-pilot completed: {len(selected_videos)} videos selected, {scheduled_count} posts scheduled',
            'activities': activities,
            'videos_selected': len(selected_videos),
            'posts_scheduled': scheduled_count
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/content-preview')
def content_preview():
    """Content preview and scheduling page - shows all videos with social media posts."""
    youtube = get_youtube_service()
    if not youtube:
        return render_template('error.html', 
                             message="YouTube API not configured. Please set up client_secret.json")
    
    try:
        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return render_template('error.html', 
                                 message="Could not find your YouTube channel. Please check authentication.")
        
        # Get all playlists
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)
        
        # Filter to Shorts playlists (or all if needed)
        shorts_playlists = [pl for pl in playlists_data if "short" in pl.get("playlistTitle", "").lower()]
        
        return render_template('content_preview.html', 
                             playlists=shorts_playlists if shorts_playlists else playlists_data)
    except Exception as e:
        import traceback
        return render_template('error.html', message=f"Error loading content preview: {str(e)}\n{traceback.format_exc()}")


@app.route('/api/content-preview/videos')
def api_content_preview_videos():
    """Get all videos with their social media posts for content preview."""
    try:
        from app.database import get_db_connection, get_video_social_posts_from_db
        from app.tagging import derive_type_enhanced, derive_role_enhanced
        
        youtube = get_youtube_service()
        if not youtube:
            return jsonify({'error': 'YouTube API not configured'}), 500
        
        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return jsonify({'error': 'Channel not found'}), 500
        
        # Get all playlists
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)
        shorts_playlists = [pl for pl in playlists_data if "short" in pl.get("playlistTitle", "").lower()]
        
        all_videos = []
        for playlist in shorts_playlists:
            videos = fetch_playlist_videos_from_youtube(youtube, playlist['playlistId'], playlist.get('channelTitle', ''))
            for video in videos:
                video_id = video['videoId']
                
                # Get social posts from database
                social_posts = get_video_social_posts_from_db(video_id)
                
                # Get video from database for metadata
                db_video = get_video(video_id)
                
                # Generate posts if not exist
                if not social_posts or len(social_posts) == 0:
                    # Generate simple posts
                    title = video.get('title', '')
                    description = video.get('description', '')
                    youtube_url = f"https://youtube.com/watch?v={video_id}"
                    
                    social_posts = {
                        'linkedin': {
                            'platform': 'linkedin',
                            'post_content': f"{title}\n\n{youtube_url}\n\n#TechInterview #CodingInterview #SystemDesign",
                            'status': 'pending',
                            'schedule_date': None
                        },
                        'facebook': {
                            'platform': 'facebook',
                            'post_content': f"{title}\n\n{youtube_url}",
                            'status': 'pending',
                            'schedule_date': None
                        },
                        'instagram': {
                            'platform': 'instagram',
                            'post_content': f"{title} {youtube_url}\n\n#TechInterview #CodingInterview #SystemDesign #LeetCode",
                            'status': 'pending',
                            'schedule_date': None
                        }
                    }
                
                all_videos.append({
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'thumbnail': video.get('thumbnail', ''),
                    'video_url': youtube_url,
                    'playlist_name': playlist.get('playlistTitle', ''),
                    'playlist_id': playlist['playlistId'],
                    'social_posts': social_posts,
                    'video_type': db_video.get('video_type', '') if db_video else '',
                    'role': db_video.get('role', '') if db_video else ''
                })
        
        return jsonify({'videos': all_videos, 'count': len(all_videos)})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


@app.route('/api/schedule-post', methods=['POST'])
def api_schedule_post():
    """Schedule a post manually with custom date/time."""
    try:
        from app.database import insert_or_update_social_post, log_activity
        
        data = request.json
        video_id = data.get('video_id')
        platform = data.get('platform')
        post_content = data.get('post_content')
        schedule_datetime = data.get('schedule_datetime')  # Format: "2026-01-15 14:00"
        
        if not all([video_id, platform, post_content, schedule_datetime]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Save to database
        insert_or_update_social_post(video_id, platform, {
            'post_content': post_content,
            'schedule_date': schedule_datetime,
            'status': 'pending'
        })
        
        # Log activity
        log_activity(
            'schedule_post',
            platform=platform,
            video_id=video_id,
            status='success',
            message=f'Manually scheduled for {schedule_datetime}',
            details={'schedule_date': schedule_datetime, 'manual': True}
        )
        
        return jsonify({
            'success': True,
            'message': f'Post scheduled for {platform} on {schedule_datetime}'
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


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
        from app.tagging import derive_type_enhanced, derive_role_enhanced, suggest_tags
        from app.database import get_video
        
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
    from app.database import get_video, get_db_connection
    from app.tagging import parse_tags, format_tags
    
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
    from app.database import get_db_connection
    from app.tagging import search_videos, parse_tags
    
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


@app.route('/content')
def content():
    """Content management page - view and schedule videos across all channels."""
    return render_template('content.html')


@app.route('/api/content/videos')
def api_content_videos():
    """API endpoint to fetch videos with social media post status for content page."""
    from app.database import get_db_connection
    import pandas as pd
    
    try:
        conn = get_db_connection()
        
        # Get all videos that are public or scheduled
        query = '''
            SELECT 
                v.video_id,
                v.title,
                v.description,
                v.tags,
                v.youtube_url,
                v.video_type,
                v.role,
                v.custom_tags,
                v.playlist_name,
                v.youtube_published_date,
                v.youtube_schedule_date,
                v.privacy_status,
                smp_linkedin.status as linkedin_status,
                smp_linkedin.schedule_date as linkedin_schedule_date,
                smp_linkedin.post_content as linkedin_post,
                smp_facebook.status as facebook_status,
                smp_facebook.schedule_date as facebook_schedule_date,
                smp_facebook.post_content as facebook_post,
                smp_instagram.status as instagram_status,
                smp_instagram.schedule_date as instagram_schedule_date,
                smp_instagram.post_content as instagram_post
            FROM videos v
            LEFT JOIN social_media_posts smp_linkedin ON v.video_id = smp_linkedin.video_id AND smp_linkedin.platform = 'linkedin'
            LEFT JOIN social_media_posts smp_facebook ON v.video_id = smp_facebook.video_id AND smp_facebook.platform = 'facebook'
            LEFT JOIN social_media_posts smp_instagram ON v.video_id = smp_instagram.video_id AND smp_instagram.platform = 'instagram'
            WHERE v.privacy_status = 'public' OR v.youtube_schedule_date IS NOT NULL
            ORDER BY COALESCE(v.youtube_schedule_date, v.youtube_published_date) DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        videos = []
        for _, row in df.iterrows():
            video = {
                'video_id': row.get('video_id', ''),
                'title': row.get('title', ''),
                'description': row.get('description', '') or '',
                'tags': row.get('tags', '') or '',
                'youtube_url': row.get('youtube_url', ''),
                'video_type': row.get('video_type', '') or '',
                'role': row.get('role', '') or '',
                'custom_tags': row.get('custom_tags', '') or '',
                'playlist_name': row.get('playlist_name', '') or '',
                'youtube_published_date': str(row.get('youtube_published_date', '')) if pd.notna(row.get('youtube_published_date')) else '',
                'youtube_schedule_date': str(row.get('youtube_schedule_date', '')) if pd.notna(row.get('youtube_schedule_date')) else '',
                'privacy_status': row.get('privacy_status', ''),
                'platforms': {
                    'linkedin': {
                        'status': row.get('linkedin_status', '') or 'not_scheduled',
                        'schedule_date': str(row.get('linkedin_schedule_date', '')) if pd.notna(row.get('linkedin_schedule_date')) else '',
                        'post_content': row.get('linkedin_post', '') or ''
                    },
                    'facebook': {
                        'status': row.get('facebook_status', '') or 'not_scheduled',
                        'schedule_date': str(row.get('facebook_schedule_date', '')) if pd.notna(row.get('facebook_schedule_date')) else '',
                        'post_content': row.get('facebook_post', '') or ''
                    },
                    'instagram': {
                        'status': row.get('instagram_status', '') or 'not_scheduled',
                        'schedule_date': str(row.get('instagram_schedule_date', '')) if pd.notna(row.get('instagram_schedule_date')) else '',
                        'post_content': row.get('instagram_post', '') or ''
                    }
                }
            }
            videos.append(video)
        
        return jsonify({'videos': videos})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc(), 'videos': []}), 500


@app.route('/api/config/platforms')
def api_config_platforms():
    """API endpoint to get configured social media platforms."""
    settings = load_settings()
    scheduling = settings.get('scheduling', {})
    platforms = scheduling.get('social_platforms', ['linkedin', 'facebook', 'instagram'])
    return jsonify({'platforms': platforms})


@app.route('/api/config/upload-client-secret', methods=['POST'])
def api_upload_client_secret():
    """API endpoint to upload client_secret.json file."""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.json'):
            return jsonify({'success': False, 'error': 'File must be a JSON file'}), 400
        
        # Read file content to validate it's a valid JSON
        try:
            content = file.read()
            json.loads(content)
            file.seek(0)  # Reset file pointer
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid JSON file'}), 400
        
        # Save to project root (parent of app directory)
        client_secret_path = os.path.join(os.path.dirname(__file__), '..', 'client_secret.json')
        client_secret_path = os.path.abspath(client_secret_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(client_secret_path), exist_ok=True)
        
        # Save the file
        file.save(client_secret_path)
        
        return jsonify({
            'success': True,
            'message': 'Client secret file uploaded successfully. Please refresh the page to see the updated status.'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


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
        has_client_id = bool(api_keys.get('linkedin_client_id'))
        has_client_secret = bool(api_keys.get('linkedin_client_secret'))
        has_token = bool(api_keys.get('linkedin_access_token'))
        has_urn = bool(api_keys.get('linkedin_person_urn'))
        
        # Either Client ID + Secret OR Access Token is required
        has_credentials = (has_client_id and has_client_secret) or has_token
        is_configured = has_credentials and has_urn
        
        return jsonify({
            'success': is_configured,
            'message': 'LinkedIn configured' if is_configured else 'Missing LinkedIn credentials (need Client ID + Secret OR Access Token, and Person URN)'
        })
    elif platform == 'facebook':
        has_app_id = bool(api_keys.get('facebook_app_id'))
        has_app_secret = bool(api_keys.get('facebook_app_secret'))
        has_token = bool(api_keys.get('facebook_page_access_token'))
        has_page_id = bool(api_keys.get('facebook_page_id'))
        
        # Either App ID + Secret OR Page Access Token is required
        has_credentials = (has_app_id and has_app_secret) or has_token
        is_configured = has_credentials and has_page_id
        
        return jsonify({
            'success': is_configured,
            'message': 'Facebook configured' if is_configured else 'Missing Facebook credentials (need App ID + Secret OR Page Access Token, and Page ID)'
        })
    elif platform == 'instagram':
        has_app_id = bool(api_keys.get('facebook_app_id'))
        has_app_secret = bool(api_keys.get('facebook_app_secret'))
        has_account = bool(api_keys.get('instagram_business_account_id'))
        has_token = bool(api_keys.get('instagram_access_token'))
        
        # Either Facebook App ID/Secret OR Instagram Access Token is required
        has_credentials = (has_app_id and has_app_secret) or has_token
        is_configured = has_credentials and has_account
        
        return jsonify({
            'success': is_configured,
            'message': 'Instagram configured' if is_configured else 'Missing Instagram credentials (need Facebook App ID + Secret OR Instagram Access Token, and Business Account ID)'
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

