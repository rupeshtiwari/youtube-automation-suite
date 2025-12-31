"""
Flask web application for YouTube automation configuration and scheduling.
Provides a web interface to configure API keys and schedule daily automation.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import json
import os
import subprocess
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Settings file
SETTINGS_FILE = 'automation_settings.json'
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
    app.run(host='0.0.0.0', port=5000, debug=True)

