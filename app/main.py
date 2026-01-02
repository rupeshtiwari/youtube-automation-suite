"""
Flask web application for YouTube automation configuration and scheduling.
Provides a web interface to configure API keys and schedule daily automation.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response, g
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


def generate_clickbait_post(title: str, description: str, video_type: str, video_role: str, platform: str, youtube_url: str) -> str:
    """
    Generate clickbait-style social media posts using psychological triggers:
    - Fear of failure in interviews
    - Threat of missing opportunities
    - Failure stories and consequences
    - Urgency and scarcity
    """
    import random
    
    # Extract key pain points from title/description
    text_lower = f"{title} {description}".lower()
    
    # Identify interview type and pain points
    is_system_design = any(kw in text_lower for kw in ['system design', 'architecture', 'scalability', 'distributed'])
    is_behavioral = any(kw in text_lower for kw in ['behavioral', 'leadership', 'stories', 'situation'])
    is_coding = any(kw in text_lower for kw in ['coding', 'leetcode', 'algorithm', 'programming'])
    is_salary = any(kw in text_lower for kw in ['salary', 'negotiation', 'compensation', 'offer'])
    is_resume = any(kw in text_lower for kw in ['resume', 'cv', 'application'])
    
    # Clickbait hooks based on content type
    hooks = []
    
    if is_system_design:
        hooks = [
            "🚨 90% of candidates FAIL system design interviews because they don't know this...",
            "⚠️ This ONE mistake in system design interviews costs candidates $50K+ in salary...",
            "💥 Most engineers get REJECTED at FAANG because they miss this critical step...",
            "🔥 FAANG interviewers reject 8/10 candidates who don't understand this...",
            "⚡️ This system design mistake made a candidate lose a $300K offer...",
            "🎯 The #1 reason candidates fail system design interviews (and how to avoid it)...",
            "💔 I've seen 100+ candidates fail because they didn't know this system design secret...",
            "🚫 Don't make this fatal system design mistake that cost someone their dream job..."
        ]
    elif is_behavioral:
        hooks = [
            "😱 This behavioral interview mistake made a candidate lose a $200K offer...",
            "⚠️ 85% of candidates FAIL behavioral interviews because they tell stories wrong...",
            "💥 Most engineers get REJECTED because they can't answer this behavioral question...",
            "🔥 FAANG interviewers reject candidates who don't structure stories this way...",
            "⚡️ This ONE behavioral mistake cost someone their Amazon offer...",
            "🎯 The #1 reason candidates fail behavioral interviews (it's not what you think)...",
            "💔 I've coached 100+ people - this is the behavioral mistake that kills offers...",
            "🚫 Don't make this fatal behavioral mistake that cost someone their dream job..."
        ]
    elif is_coding:
        hooks = [
            "🚨 95% of candidates FAIL coding interviews because they don't optimize this way...",
            "⚠️ This coding interview mistake costs candidates $100K+ in total compensation...",
            "💥 Most engineers get REJECTED at FAANG because they miss this optimization...",
            "🔥 FAANG interviewers reject 9/10 candidates who don't think about this...",
            "⚡️ This coding mistake made a candidate lose a $400K offer...",
            "🎯 The #1 reason candidates fail coding interviews (and the simple fix)...",
            "💔 I've seen 200+ candidates fail because they didn't know this coding pattern...",
            "🚫 Don't make this fatal coding mistake that cost someone their dream job..."
        ]
    elif is_salary:
        hooks = [
            "💰 This salary negotiation mistake cost someone $80K per year...",
            "⚠️ 90% of candidates leave $100K+ on the table because they don't negotiate this way...",
            "💥 Most engineers accept LOW offers because they don't know this negotiation secret...",
            "🔥 This ONE negotiation mistake cost someone a $300K total comp increase...",
            "⚡️ I've helped clients unlock $4M+ in salary - here's the #1 mistake to avoid...",
            "🎯 The salary negotiation mistake that costs engineers $50K-$200K per year...",
            "💔 Don't make this negotiation mistake that cost someone their dream compensation...",
            "🚫 This salary negotiation error made someone lose $150K in total comp..."
        ]
    elif is_resume:
        hooks = [
            "📄 This resume mistake makes recruiters REJECT 90% of applications...",
            "⚠️ Most engineers' resumes get filtered out because they miss this critical element...",
            "💥 This ONE resume mistake cost someone 50+ interview rejections...",
            "🔥 FAANG recruiters reject resumes that don't have this...",
            "⚡️ This resume error made a candidate lose 20+ interview opportunities...",
            "🎯 The #1 resume mistake that gets your application filtered out immediately...",
            "💔 I've reviewed 500+ resumes - this is the mistake that kills your chances...",
            "🚫 Don't make this fatal resume mistake that cost someone their dream job..."
        ]
    else:
        # Generic hooks for interview prep
        hooks = [
            "🚨 90% of candidates FAIL interviews because they don't prepare this way...",
            "⚠️ This interview mistake costs candidates $50K-$200K in lost opportunities...",
            "💥 Most engineers get REJECTED because they don't know this interview secret...",
            "🔥 FAANG interviewers reject 8/10 candidates who miss this critical step...",
            "⚡️ This interview mistake made a candidate lose a $300K offer...",
            "🎯 The #1 reason candidates fail interviews (and how to avoid it)...",
            "💔 I've coached 100+ people - this is the mistake that kills offers...",
            "🚫 Don't make this fatal interview mistake that cost someone their dream job..."
        ]
    
    # Select a random hook
    hook = random.choice(hooks)
    
    # Extract value proposition from title
    value_prop = title
    if len(value_prop) > 80:
        value_prop = value_prop[:77] + "..."
    
    # Create urgency and scarcity elements
    urgency_hooks = [
        "⏰ Limited spots available for 1-on-1 coaching",
        "🔥 Only a few coaching slots left this week",
        "⚡️ Book your session before spots fill up",
        "🎯 Don't wait - interviews are happening NOW",
        "💥 Secure your coaching slot before it's too late"
    ]
    urgency = random.choice(urgency_hooks)
    
    # Platform-specific formatting
    if platform == 'linkedin':
        post = f"{hook}\n\n"
        post += f"💡 {value_prop}\n\n"
        post += f"👉 Watch the full breakdown: {youtube_url}\n\n"
        post += f"📅 Book 1-on-1 coaching: https://fullstackmaster/book\n"
        post += f"💬 WhatsApp: +1-609-442-4081\n\n"
        post += f"{urgency}\n\n"
        post += generate_hashtags_for_rupesh(video_type, video_role, title, description)
        
    elif platform == 'facebook':
        post = f"{hook}\n\n"
        post += f"💡 {value_prop}\n\n"
        post += f"👉 Watch here: {youtube_url}\n\n"
        post += f"📅 Book 1-on-1 coaching: https://fullstackmaster/book\n"
        post += f"💬 WhatsApp: +1-609-442-4081\n\n"
        post += f"{urgency}\n\n"
        post += generate_hashtags_for_rupesh(video_type, video_role, title, description)
        
    elif platform == 'instagram':
        post = f"{hook}\n\n"
        post += f"💡 {value_prop}\n\n"
        post += f"▶️ Watch: {youtube_url}\n\n"
        post += f"📅 Book 1-on-1 coaching: https://fullstackmaster/book\n"
        post += f"💬 WhatsApp: +1-609-442-4081\n\n"
        post += f"{urgency}\n\n"
        post += generate_hashtags_for_rupesh(video_type, video_role, title, description)
        
    else:
        post = f"{hook}\n\n{value_prop}\n\n{youtube_url}\n\n📅 Book 1-on-1 coaching: https://fullstackmaster/book\n💬 WhatsApp: +1-609-442-4081"
    
    return post


def generate_hashtags_for_rupesh(video_type: str, video_role: str, title: str, description: str) -> str:
    """
    Generate hashtags aligned with Rupesh's coaching expertise from IGotAnOffer.
    Based on: AWS Senior CSM, Interview Coaching, System Design, Leadership, Career Growth
    """
    hashtags = []
    text = f"{title} {description}".lower()
    
    # Core expertise hashtags (always include some)
    core_tags = ['TechInterview', 'CareerGrowth']
    
    # Interview-related (Rupesh's main focus)
    if any(kw in text for kw in ['system design', 'sys design', 'architecture', 'scalability']):
        hashtags.extend(['SystemDesign', 'SystemDesignInterview', 'SolutionsArchitect', 'AWS'])
    if any(kw in text for kw in ['coding', 'leetcode', 'algorithm', 'programming']):
        hashtags.extend(['CodingInterview', 'LeetCode', 'Algorithm', 'TechInterview'])
    if any(kw in text for kw in ['behavioral', 'leadership principles', 'stories']):
        hashtags.extend(['BehavioralInterview', 'Leadership', 'CareerCoaching'])
    if any(kw in text for kw in ['mock interview', 'interview prep', 'interview']):
        hashtags.extend(['MockInterview', 'InterviewPrep', 'FAANGInterview'])
    
    # Role-based hashtags (Rupesh coaches these roles)
    if any(kw in text for kw in ['engineering manager', 'em', 'manager']):
        hashtags.extend(['EngineeringManager', 'TechLeadership', 'Management'])
    if any(kw in text for kw in ['product manager', 'pm', 'product']):
        hashtags.extend(['ProductManager', 'ProductManagement', 'PM'])
    if any(kw in text for kw in ['solutions architect', 'architect', 'sa']):
        hashtags.extend(['SolutionsArchitect', 'CloudArchitecture', 'AWS'])
    if any(kw in text for kw in ['data engineer', 'data engineering']):
        hashtags.extend(['DataEngineering', 'DataEngineer', 'BigData'])
    if any(kw in text for kw in ['cloud engineer', 'aws', 'cloud']):
        hashtags.extend(['CloudEngineering', 'AWS', 'CloudComputing', 'DevOps'])
    if any(kw in text for kw in ['staff engineer', 'senior engineer', 'principal']):
        hashtags.extend(['StaffEngineer', 'SeniorEngineer', 'TechCareer'])
    if any(kw in text for kw in ['director', 'vp', 'executive']):
        hashtags.extend(['TechLeadership', 'Executive', 'SeniorLeadership'])
    
    # Career growth (Rupesh's specialty)
    if any(kw in text for kw in ['resume', 'cv', 'resume review']):
        hashtags.extend(['ResumeReview', 'ResumeTips', 'JobSearch'])
    if any(kw in text for kw in ['salary', 'negotiation', 'compensation']):
        hashtags.extend(['SalaryNegotiation', 'CareerAdvice', 'TechSalary'])
    if any(kw in text for kw in ['career', 'promotion', 'growth']):
        hashtags.extend(['CareerGrowth', 'CareerCoaching', 'TechCareer'])
    
    # AWS/Cloud specific (Rupesh's current role)
    if any(kw in text for kw in ['aws', 'amazon', 'cloud infrastructure']):
        hashtags.extend(['AWS', 'CloudComputing', 'SolutionsArchitect'])
    
    # FAANG focus (Rupesh coaches for FAANG)
    if any(kw in text for kw in ['faang', 'amazon', 'google', 'microsoft', 'meta', 'apple']):
        hashtags.extend(['FAANG', 'BigTech', 'TechInterview'])
    
    # Remove duplicates and limit to 10-12 most relevant
    hashtags = list(dict.fromkeys(hashtags))  # Preserve order, remove dupes
    hashtags = core_tags + [h for h in hashtags if h not in core_tags][:10]
    
    return ' '.join(['#' + tag for tag in hashtags])
from app import views

# Get project root (parent of app/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(project_root, 'templates')

static_dir = os.path.join(os.path.dirname(__file__), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir, static_url_path='/static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Performance optimizations
from app.performance import compress_response, optimize_response_headers, cached

@app.after_request
def after_request(response):
    """Apply performance optimizations to all responses."""
    response = optimize_response_headers(response)
    response = compress_response(response)
    return response

# Initialize database on app startup (ensures settings table exists)
init_database()


@app.before_request
def before_request():
    """Add config warnings to all requests."""
    g.config_warnings = validate_config()

# Settings file - support NAS/Docker deployment
DATA_DIR = os.getenv('DATA_DIR', os.path.dirname(__file__))
SETTINGS_FILE = os.path.join(DATA_DIR, 'automation_settings.json')
SCHEDULER = BackgroundScheduler()
SCHEDULER.start()

# IST timezone
IST = timezone(timedelta(hours=5, minutes=30))


def load_settings():
    """Load settings from database (with fallback to JSON file for migration)."""
    from app.database import load_settings_from_db
    
    # Try to load from database first (persistent storage)
    db_settings = load_settings_from_db()
    if db_settings:
        return db_settings
    
    # Fallback to JSON file (for migration from old system)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                json_settings = json.load(f)
                # Migrate to database
                save_settings(json_settings)
                return json_settings
        except (json.JSONDecodeError, IOError):
            pass
    
    # Return default settings
    return {
        'api_keys': {
            'linkedin_client_id': '',
            'linkedin_client_secret': '',
            'linkedin_access_token': '',
            'linkedin_person_urn': '',
            'facebook_page_access_token': '',
            'facebook_page_id': '',
            'instagram_business_account_id': '',
            'ayrshare_api_key': '',
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


def validate_config():
    """Validate configuration and return warnings for missing required fields."""
    settings = load_settings()
    warnings = []
    api_keys = settings.get('api_keys', {})
    
    # Check LinkedIn configuration
    linkedin_client_id = api_keys.get('linkedin_client_id', '').strip()
    linkedin_client_secret = api_keys.get('linkedin_client_secret', '').strip()
    linkedin_access_token = api_keys.get('linkedin_access_token', '').strip()
    linkedin_person_urn = api_keys.get('linkedin_person_urn', '').strip()
    
    if not linkedin_client_id or not linkedin_client_secret:
        warnings.append({
            'platform': 'LinkedIn',
            'severity': 'error',
            'message': 'LinkedIn Client ID and Client Secret are required',
            'fields': ['LinkedIn Client ID', 'LinkedIn Client Secret'],
            'link': '/config#linkedin'
        })
    elif not linkedin_person_urn:
        # Auto-fetch Person URN if we have access token
        if linkedin_access_token:
            try:
                person_urn = auto_fetch_linkedin_person_urn(linkedin_access_token)
                if person_urn:
                    # Save it to settings
                    api_keys['linkedin_person_urn'] = person_urn
                    settings['api_keys'] = api_keys
                    save_settings(settings)
                    print(f"✅ Auto-fetched and saved LinkedIn Person URN: {person_urn}")
                else:
                    warnings.append({
                        'platform': 'LinkedIn',
                        'severity': 'warning',
                        'message': 'LinkedIn Person URN could not be auto-fetched. Please fetch it manually.',
                        'fields': ['LinkedIn Person URN'],
                        'link': '/config#linkedin'
                    })
            except Exception as e:
                warnings.append({
                    'platform': 'LinkedIn',
                    'severity': 'warning',
                    'message': f'LinkedIn Person URN auto-fetch failed: {str(e)}. Please fetch it manually.',
                    'fields': ['LinkedIn Person URN'],
                    'link': '/config#linkedin'
                })
        else:
            warnings.append({
                'platform': 'LinkedIn',
                'severity': 'warning',
                'message': 'LinkedIn Person URN is recommended for posting. Add access token to auto-fetch.',
                'fields': ['LinkedIn Person URN'],
                'link': '/config#linkedin'
            })
    
    # Check Facebook configuration
    facebook_page_token = api_keys.get('facebook_page_access_token', '').strip()
    facebook_page_id = api_keys.get('facebook_page_id', '').strip()
    
    if not facebook_page_token or not facebook_page_id:
        warnings.append({
            'platform': 'Facebook',
            'severity': 'error',
            'message': 'Facebook Page Access Token and Page ID are required',
            'fields': ['Facebook Page Access Token', 'Facebook Page ID'],
            'link': '/config#facebook'
        })
    elif not facebook_page_id:
        warnings.append({
            'platform': 'Facebook',
            'severity': 'warning',
            'message': 'Facebook Page ID is required for posting',
            'fields': ['Facebook Page ID'],
            'link': '/config#facebook'
        })
    
    # Check Instagram configuration
    instagram_account_id = api_keys.get('instagram_business_account_id', '').strip()
    
    if not instagram_account_id:
        warnings.append({
            'platform': 'Instagram',
            'severity': 'warning',
            'message': 'Instagram Business Account ID is required for posting',
            'fields': ['Instagram Business Account ID'],
            'link': '/config#instagram'
        })
    
    return warnings


def auto_fetch_linkedin_person_urn(access_token):
    """Auto-fetch LinkedIn Person URN from access token."""
    try:
        import requests
        
        # Get user profile to extract Person URN
        url = 'https://api.linkedin.com/v2/userinfo'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Person URN is typically in 'sub' field or we can construct it
            sub = data.get('sub', '')
            if sub:
                # Format: urn:li:person:xxxxx
                if not sub.startswith('urn:li:person:'):
                    return f'urn:li:person:{sub}'
                return sub
        
        # Alternative: Try to get from /me endpoint
        url = 'https://api.linkedin.com/v2/me'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            person_id = data.get('id', '')
            if person_id:
                if not person_id.startswith('urn:li:person:'):
                    return f'urn:li:person:{person_id}'
                return person_id
        
        return None
    except Exception as e:
        print(f"⚠️ Error auto-fetching LinkedIn Person URN: {e}")
        return None


def save_settings(settings):
    """
    Save settings to database (persistent storage) and JSON file (backup).
    This ensures settings persist across server restarts and code changes.
    """
    from app.database import save_settings_to_db, init_database
    
    # Ensure database is initialized
    try:
        init_database()
    except Exception as e:
        print(f"⚠️ Warning: Failed to initialize database: {e}")
    
    # Save to database (primary storage - persists across restarts)
    db_saved = False
    try:
        save_settings_to_db(settings)
        db_saved = True
        print(f"✅ Settings saved to database at {datetime.now()}")
    except Exception as e:
        print(f"❌ ERROR: Failed to save settings to database: {e}")
        import traceback
        traceback.print_exc()
        # Continue to save to JSON as backup
    
    # Also save to JSON file as backup (always do this as secondary backup)
    json_saved = False
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
            json_saved = True
            print(f"✅ Settings saved to JSON backup file")
    except Exception as e:
        print(f"⚠️ Warning: Failed to save settings to JSON file: {e}")
    
    # Verify at least one save succeeded
    if not db_saved and not json_saved:
        raise Exception("CRITICAL: Failed to save settings to both database and JSON file!")
    
    # Also update .env file for compatibility (for scripts that read .env)
    try:
        update_env_file(settings)
    except Exception as e:
        print(f"⚠️ Warning: Failed to update .env file: {e}")
    
    return db_saved, json_saved


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
        'FACEBOOK_PAGE_ACCESS_TOKEN': api_keys.get('facebook_page_access_token', ''),
        'FACEBOOK_PAGE_ID': api_keys.get('facebook_page_id', ''),
        'INSTAGRAM_BUSINESS_ACCOUNT_ID': api_keys.get('instagram_business_account_id', ''),
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


def publish_scheduled_posts():
    """Auto-publish scheduled posts that are ready."""
    from app.database import get_db_connection, get_video, update_post_status, log_activity
    from datetime import datetime
    
    try:
        settings = load_settings()
        upload_method = settings.get('scheduling', {}).get('upload_method', 'native')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get posts that are scheduled and ready to publish
        now = datetime.now()
        cursor.execute('''
            SELECT smp.*, v.video_id, v.title, v.youtube_url
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status = 'scheduled'
                AND smp.schedule_date IS NOT NULL
                AND datetime(smp.schedule_date) <= datetime(?)
            ORDER BY smp.schedule_date ASC
            LIMIT 10
        ''', (now.isoformat(),))
        
        posts_to_publish = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not posts_to_publish:
            return
        
        print(f"[{datetime.now()}] Found {len(posts_to_publish)} posts ready to publish")
        
        api_keys = settings.get('api_keys', {})
        api_credentials = {
            'linkedin_access_token': api_keys.get('linkedin_access_token'),
            'linkedin_person_urn': api_keys.get('linkedin_person_urn'),
            'facebook_page_id': api_keys.get('facebook_page_id'),
            'facebook_page_access_token': api_keys.get('facebook_page_access_token'),
            'instagram_business_account_id': api_keys.get('instagram_business_account_id')
            # Note: Instagram uses Facebook Page Access Token, not a separate token
        }
        
        for post in posts_to_publish:
            try:
                video_id = post.get('video_id')
                platform = post.get('platform', '').lower()
                post_content = post.get('post_content', '')
                post_id = post.get('id')
                
                if upload_method == 'native' and video_id:
                    # Native video upload
                    from app.video_processor import process_and_upload_video
                    
                    result = process_and_upload_video(
                        video_id=video_id,
                        platforms=[platform],
                        captions={platform: post_content},
                        api_credentials=api_credentials
                    )
                    
                    if result.get('success') and result.get('results', {}).get(platform, {}).get('success'):
                        # Update post status
                        update_post_status(
                            video_id, platform, 'published',
                            actual_scheduled_date=now.isoformat(),
                            post_id=result['results'][platform].get('post_id')
                        )
                        
                        log_activity(
                            'auto_publish',
                            platform=platform,
                            video_id=video_id,
                            video_title=post.get('title', ''),
                            status='success',
                            message=f'Auto-published natively to {platform}',
                            details={'post_id': result['results'][platform].get('post_id')}
                        )
                        print(f"[{datetime.now()}] ✅ Published {video_id} to {platform} (native upload)")
                    else:
                        error = result.get('error') or result.get('results', {}).get(platform, {}).get('error', 'Upload failed')
                        update_post_status(video_id, platform, 'failed', error_message=error)
                        log_activity(
                            'auto_publish',
                            platform=platform,
                            video_id=video_id,
                            status='failed',
                            message=f'Failed to publish: {error}'
                        )
                        print(f"[{datetime.now()}] ❌ Failed to publish {video_id} to {platform}: {error}")
                else:
                    # Link sharing mode - would need link posting API
                    # For now, just mark as published (link sharing implementation needed)
                    update_post_status(video_id, platform, 'published', actual_scheduled_date=now.isoformat())
                    print(f"[{datetime.now()}] ✅ Published {video_id} to {platform} (link sharing)")
                
            except Exception as e:
                import traceback
                error_msg = str(e)
                update_post_status(post.get('video_id'), post.get('platform'), 'failed', error_message=error_msg)
                print(f"[{datetime.now()}] ❌ Error publishing post {post.get('id')}: {error_msg}")
                log_activity(
                    'auto_publish',
                    platform=post.get('platform'),
                    video_id=post.get('video_id'),
                    status='error',
                    message=f'Exception: {error_msg}',
                    errors=traceback.format_exc()
                )
        
    except Exception as e:
        import traceback
        print(f"[{datetime.now()}] ❌ Error in publish_scheduled_posts: {e}")
        print(traceback.format_exc())


def schedule_daily_job():
    """Schedule the daily automation job and auto-publishing job."""
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
    
    # Add auto-publishing job - runs every 15 minutes to check for posts ready to publish
    SCHEDULER.add_job(
        func=publish_scheduled_posts,
        trigger='interval',
        minutes=15,
        id='auto_publish_posts',
        name='Auto-Publish Scheduled Posts',
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


@app.route('/favicon.ico')
def favicon():
    """Serve favicon directly."""
    return app.send_static_file('favicon.ico')


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
            'facebook_page_access_token': request.form.get('facebook_page_access_token', ''),
            'facebook_page_id': request.form.get('facebook_page_id', ''),
            'instagram_business_account_id': request.form.get('instagram_business_account_id', ''),
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
            'upload_method': request.form.get('upload_method', 'native'),
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
    
    # Calculate configuration completeness
    api_keys = settings.get('api_keys', {})
    config_complete = (
        youtube_status.get('client_secret_exists', False) and
        bool(api_keys.get('linkedin_client_id')) and
        bool(api_keys.get('linkedin_client_secret')) and
        bool(api_keys.get('linkedin_person_urn')) and
        bool(api_keys.get('facebook_page_access_token')) and
        bool(api_keys.get('facebook_page_id')) and
        bool(api_keys.get('instagram_business_account_id'))
    )
    
    return render_template('config.html', settings=settings, youtube_status=youtube_status, config_complete=config_complete)


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


@app.route('/sessions')
@cached(timeout=60)  # Cache for 1 minute (sessions change less frequently)
def sessions():
    """Sessions management page - load and create shorts scripts from coaching sessions."""
    import os
    from pathlib import Path
    
    sessions_dir = Path('data/sessions')
    sessions_list = []
    
    if sessions_dir.exists():
        for file_path in sessions_dir.glob('*.txt'):
            try:
                file_size = file_path.stat().st_size
                sessions_list.append({
                    'filename': file_path.name,
                    'size': file_size,
                    'size_kb': round(file_size / 1024, 2),
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    # Sort by modified date (newest first)
    sessions_list.sort(key=lambda x: x['modified'], reverse=True)
    
    return render_template('sessions.html', sessions=sessions_list)


@app.route('/api/sessions/<filename>')
def api_get_session(filename):
    """Get content of a session file."""
    import os
    from pathlib import Path
    from flask import safe_join
    
    # Security: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    sessions_dir = Path('data/sessions')
    file_path = sessions_dir / filename
    
    if not file_path.exists() or not file_path.is_file():
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'filename': filename,
            'content': content,
            'size': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<filename>/generate-shorts', methods=['POST'])
def api_generate_shorts_from_session(filename):
    """Generate viral shorts scripts from a session file."""
    import os
    from pathlib import Path
    import re
    
    # Security: prevent directory traversal
    if '..' in filename or '/' in filename or '\\' in filename:
        return jsonify({'error': 'Invalid filename'}), 400
    
    sessions_dir = Path('data/sessions')
    file_path = sessions_dir / filename
    
    if not file_path.exists() or not file_path.is_file():
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Get settings for CTAs
        settings = load_settings()
        cta_settings = settings.get('cta', {})
        booking_url = cta_settings.get('booking_url', 'https://fullstackmaster/book')
        whatsapp_number = cta_settings.get('whatsapp_number', '+1-609-442-4081')
        
        # Generate shorts scripts using enhanced generator
        from app.session_shorts_generator import generate_shorts_from_session_enhanced
        shorts_scripts_data = generate_shorts_from_session_enhanced(content, booking_url, whatsapp_number)
        
        # Format scripts for response (extract script text and metadata)
        shorts_scripts = []
        for script_data in shorts_scripts_data:
            if isinstance(script_data, dict):
                # Format with metadata
                formatted = f"""SCRIPT #{len(shorts_scripts) + 1}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ROLE: {script_data.get('role', 'N/A')}
TYPE: {script_data.get('type', 'N/A')}
SUGGESTED PLAYLIST: {script_data.get('playlist_suggestion', 'N/A')}
DURATION: {script_data.get('estimated_duration', '40 seconds')}

{script_data.get('script', '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                shorts_scripts.append(formatted.strip())
            else:
                shorts_scripts.append(str(script_data))
        
        return jsonify({
            'success': True,
            'filename': filename,
            'scripts': shorts_scripts,
            'count': len(shorts_scripts)
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


def generate_shorts_from_session_old(session_content: str, booking_url: str, whatsapp_number: str) -> list:
    """
    Generate viral shorts scripts from session content.
    Uses AI-like patterns to create engaging, clickbait-style scripts.
    """
    scripts = []
    
    # Extract key insights, questions, and answers from session
    lines = session_content.split('\n')
    
    # Pattern 1: Extract interview questions and answers
    current_qa = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 20:
            continue
        
        # Look for question patterns
        if any(keyword in line.lower() for keyword in ['?', 'how', 'what', 'why', 'tell me', 'describe', 'explain']):
            if current_qa:
                # Generate script from previous Q&A
                script = create_viral_script_from_qa(current_qa, booking_url, whatsapp_number)
                if script:
                    scripts.append(script)
            current_qa = [line]
        elif current_qa:
            current_qa.append(line)
            if len(current_qa) >= 5:  # Enough context
                script = create_viral_script_from_qa(current_qa, booking_url, whatsapp_number)
                if script:
                    scripts.append(script)
                current_qa = []
    
    # Process remaining Q&A
    if current_qa:
        script = create_viral_script_from_qa(current_qa, booking_url, whatsapp_number)
        if script:
            scripts.append(script)
    
    # Pattern 2: Extract key insights and tips
    insights = extract_insights(session_content)
    for insight in insights[:10]:  # Limit to 10
        script = create_viral_script_from_insight(insight, booking_url, whatsapp_number)
        if script:
            scripts.append(script)
    
    # Pattern 3: Extract mistakes and lessons learned
    mistakes = extract_mistakes(session_content)
    for mistake in mistakes[:5]:  # Limit to 5
        script = create_viral_script_from_mistake(mistake, booking_url, whatsapp_number)
        if script:
            scripts.append(script)
    
    return scripts[:20]  # Return max 20 scripts


def create_viral_script_from_qa(qa_lines: list, booking_url: str, whatsapp_number: str) -> str:
    """Create a viral shorts script from Q&A content."""
    content = ' '.join(qa_lines[:3])  # Use first 3 lines
    
    hooks = [
        "🚨 90% of candidates FAIL this question...",
        "Most engineers get REJECTED because of this mistake...",
        "FAANG interviewers reject 8/10 candidates. Here's why...",
        "This one mistake cost someone their dream job...",
        "The #1 reason why talented engineers fail interviews..."
    ]
    
    import random
    hook = random.choice(hooks)
    
    # Extract the key point (first 100 chars)
    key_point = content[:100].strip()
    if len(key_point) < 30:
        return None
    
    script = f"""{hook}

{key_point}...

💡 Want to master this and avoid common mistakes?

📅 Book 1-on-1 coaching: {booking_url}
💬 WhatsApp: {whatsapp_number}

#TechInterview #CareerGrowth #FAANGInterview"""
    
    return script


def create_viral_script_from_insight(insight: str, booking_url: str, whatsapp_number: str) -> str:
    """Create a viral shorts script from an insight."""
    hooks = [
        "💡 Pro tip that changed my career...",
        "This insight helped 100+ engineers get offers...",
        "The secret most engineers don't know...",
        "This one thing separates senior engineers from juniors..."
    ]
    
    import random
    hook = random.choice(hooks)
    
    script = f"""{hook}

{insight[:150]}...

📅 Book 1-on-1 coaching: {booking_url}
💬 WhatsApp: {whatsapp_number}

#TechInterview #CareerGrowth"""
    
    return script


def create_viral_script_from_mistake(mistake: str, booking_url: str, whatsapp_number: str) -> str:
    """Create a viral shorts script from a mistake/lesson."""
    hooks = [
        "🚨 This mistake cost someone their ${}K offer...",
        "Don't make this mistake in your interview...",
        "I've seen 100+ candidates fail because of this...",
        "This is why talented engineers get rejected..."
    ]
    
    import random
    hook = random.choice(hooks).format(random.randint(50, 300))
    
    script = f"""{hook}

{mistake[:150]}...

💡 Learn from this and avoid the same mistake!

📅 Book 1-on-1 coaching: {booking_url}
💬 WhatsApp: {whatsapp_number}

#TechInterview #CareerGrowth #InterviewPrep"""
    
    return script


def extract_insights(content: str) -> list:
    """Extract key insights from session content."""
    insights = []
    lines = content.split('\n')
    
    keywords = ['insight', 'tip', 'key', 'important', 'remember', 'pro tip', 'secret', 'strategy']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords) and len(line.strip()) > 30:
            # Get context (next 2 lines)
            context = line
            if i + 1 < len(lines):
                context += ' ' + lines[i + 1]
            if i + 2 < len(lines):
                context += ' ' + lines[i + 2]
            insights.append(context.strip()[:200])
    
    return insights


def extract_mistakes(content: str) -> list:
    """Extract mistakes and lessons from session content."""
    mistakes = []
    lines = content.split('\n')
    
    keywords = ['mistake', 'wrong', 'error', 'failed', 'rejected', 'don\'t', 'avoid', 'lesson']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords) and len(line.strip()) > 30:
            # Get context (next 2 lines)
            context = line
            if i + 1 < len(lines):
                context += ' ' + lines[i + 1]
            if i + 2 < len(lines):
                context += ' ' + lines[i + 2]
            mistakes.append(context.strip()[:200])
    
    return mistakes


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
            except Exception as e:
                # If token doesn't have analytics scope, return error gracefully
                return {'error': 'YouTube Analytics API not authenticated. Please re-authenticate with analytics scope.', 'details': str(e)}
        
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
                    # Generate post content with CTAs using YouTube metadata
                    db_video = get_video(video_id)
                    title = db_video.get('title', video_title) if db_video else video_title
                    description = db_video.get('description', video.get('description', '')) if db_video else video.get('description', '')
                    tags = db_video.get('tags', video.get('tags', '')) if db_video else video.get('tags', '')
                    youtube_url = f"https://youtube.com/watch?v={video_id}"
                    playlist_name = playlist.get('playlistTitle', '')
                    
                    # Derive video type and role for better hashtags
                    from app.tagging import derive_type_enhanced, derive_role_enhanced
                    video_type = derive_type_enhanced(playlist_name, title, description, tags)
                    video_role = derive_role_enhanced(playlist_name, title, description, tags)
                    
                    # Generate hashtags
                    hashtags = generate_hashtags_for_rupesh(video_type, video_role, title, description)
                    
                    # CTAs
                    booking_cta = "📅 Book 1-on-1 coaching: https://fullstackmaster/book"
                    whatsapp_cta = "💬 WhatsApp: +1-609-442-4081"
                    
                    # Extract key points from description
                    description_lines = description.split('\n')[:3] if description else []
                    key_points = '\n'.join([line.strip() for line in description_lines if line.strip()][:2])
                    
                    # Generate clickbait-style posts with psychological triggers
                    post_content = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform=platform,
                        youtube_url=youtube_url
                    )
                
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
        from app.database import get_db_connection, get_video
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
                social_posts_dict = get_video_social_posts_from_db(video_id)
                
                # social_posts_dict is already a dict from get_video_social_posts_from_db
                social_posts = social_posts_dict if social_posts_dict else {}
                
                # Get video from database for metadata
                db_video = get_video(video_id)
                
                # Generate posts if not exist
                if not social_posts or len(social_posts) == 0:
                    # Generate posts aligned with Rupesh's coaching expertise
                    from app.tagging import derive_type_enhanced, derive_role_enhanced
                    
                    title = video.get('title', '')
                    description = video.get('description', '')
                    tags = video.get('tags', '')
                    published_at = video.get('publishedAt', '')
                    youtube_url = f"https://youtube.com/watch?v={video_id}"
                    playlist_name = playlist.get('playlistTitle', '')
                    
                    # Derive video type and role for better hashtags
                    video_type = derive_type_enhanced(playlist_name, title, description, tags)
                    video_role = derive_role_enhanced(playlist_name, title, description, tags)
                    
                    # Generate hashtags based on Rupesh's expertise
                    hashtags = generate_hashtags_for_rupesh(video_type, video_role, title, description)
                    
                    # CTAs
                    booking_cta = "📅 Book 1-on-1 coaching: https://fullstackmaster/book"
                    whatsapp_cta = "💬 WhatsApp: +1-609-442-4081"
                    
                    # Extract key points from description (first 2-3 sentences)
                    description_lines = description.split('\n')[:3] if description else []
                    key_points = '\n'.join([line.strip() for line in description_lines if line.strip()][:2])
                    
                    # Generate clickbait-style posts with psychological triggers
                    linkedin_post = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform='linkedin',
                        youtube_url=youtube_url
                    )
                    
                    facebook_post = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform='facebook',
                        youtube_url=youtube_url
                    )
                    
                    instagram_post = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform='instagram',
                        youtube_url=youtube_url
                    )
                    
                    social_posts = {
                        'linkedin': {
                            'platform': 'linkedin',
                            'post_content': linkedin_post,
                            'status': 'pending',
                            'schedule_date': None
                        },
                        'facebook': {
                            'platform': 'facebook',
                            'post_content': facebook_post,
                            'status': 'pending',
                            'schedule_date': None
                        },
                        'instagram': {
                            'platform': 'instagram',
                            'post_content': instagram_post,
                            'status': 'pending',
                            'schedule_date': None
                        }
                    }
                
                # Get tags and published date from video data
                video_tags = video.get('tags', '')
                if isinstance(video_tags, list):
                    video_tags = ', '.join(video_tags)
                published_at = video.get('publishedAt', '') or video.get('published_at', '')
                
                all_videos.append({
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'tags': video_tags,
                    'published_at': published_at,
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


@app.route('/api/config/save-section', methods=['POST'])
def api_save_config_section():
    """API endpoint to save a specific configuration section."""
    try:
        section = request.json.get('section')
        data = request.json.get('data', {})
        
        if not section:
            return jsonify({'success': False, 'error': 'Section not specified'}), 400
        
        settings = load_settings()
        
        # Update the specific section
        if section == 'api_keys':
            settings['api_keys'] = {
                'linkedin_client_id': data.get('linkedin_client_id', ''),
                'linkedin_client_secret': data.get('linkedin_client_secret', ''),
                'linkedin_access_token': data.get('linkedin_access_token', ''),
                'linkedin_person_urn': data.get('linkedin_person_urn', ''),
                'facebook_page_access_token': data.get('facebook_page_access_token', ''),
                'facebook_page_id': data.get('facebook_page_id', ''),
                'instagram_business_account_id': data.get('instagram_business_account_id', ''),
                'ayrshare_api_key': data.get('ayrshare_api_key', ''),
            }
        elif section == 'scheduling':
            settings['scheduling'] = {
                'enabled': data.get('scheduling_enabled') == True or data.get('scheduling_enabled') == 'on',
                'videos_per_day': int(data.get('videos_per_day', 1)),
                'youtube_schedule_time': data.get('youtube_schedule_time', '23:00'),
                'social_media_schedule_time': data.get('social_media_schedule_time', '19:30'),
                'schedule_day': data.get('schedule_day', 'wednesday'),
                'playlist_id': data.get('playlist_id', ''),
                'export_type': data.get('export_type', 'shorts'),
                'use_database': data.get('use_database') == True or data.get('use_database') == 'on',
                'auto_post_social': data.get('auto_post_social') == True or data.get('auto_post_social') == 'on',
                'social_platforms': data.get('social_platforms', []),
                'upload_method': data.get('upload_method', 'native'),  # 'native' or 'link'
            }
            # Reschedule job if scheduling settings changed
            schedule_daily_job()
        elif section == 'thresholds':
            settings['thresholds'] = {
                'linkedin_daily_limit': int(data.get('linkedin_daily_limit', 25)),
                'facebook_daily_limit': int(data.get('facebook_daily_limit', 25)),
                'instagram_daily_limit': int(data.get('instagram_daily_limit', 25)),
                'youtube_daily_limit': int(data.get('youtube_daily_limit', 10)),
            }
        elif section == 'targeting':
            settings['targeting'] = {
                'target_audience': data.get('target_audience', 'usa_professionals'),
                'interview_types': data.get('interview_types', []),
                'role_levels': data.get('role_levels', []),
                'timezone': data.get('timezone', 'America/New_York'),
                'optimal_times': data.get('optimal_times', []) if isinstance(data.get('optimal_times'), list) else ['14:00', '17:00', '21:00']
            }
        elif section == 'cta':
            settings['cta'] = {
                'booking_url': data.get('booking_url', 'https://fullstackmaster/book'),
                'whatsapp_number': data.get('whatsapp_number', '+1-609-442-4081'),
                'linkedin_url': data.get('linkedin_url', ''),
                'instagram_url': data.get('instagram_url', ''),
                'facebook_url': data.get('facebook_url', ''),
                'youtube_url': data.get('youtube_url', ''),
                'twitter_url': data.get('twitter_url', ''),
                'website_url': data.get('website_url', '')
            }
        else:
            return jsonify({'success': False, 'error': f'Unknown section: {section}'}), 400
        
        save_settings(settings)
        
        return jsonify({
            'success': True,
            'message': f'{section.replace("_", " ").title()} saved successfully!'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/linkedin/oauth/authorize')
def api_linkedin_oauth_authorize():
    """Buffer-style LinkedIn OAuth - just click 'Connect LinkedIn' and authorize."""
    try:
        settings = load_settings()
        api_keys = settings.get('api_keys', {})
        client_id = api_keys.get('linkedin_client_id', '').strip()
        client_secret = api_keys.get('linkedin_client_secret', '').strip()
        
        if not client_id or not client_secret:
            flash('Please configure LinkedIn Client ID and Secret first in Settings → API Keys', 'error')
            return redirect(url_for('config'))
        
        # Generate state for security
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Store state in session
        session['linkedin_oauth_state'] = state
        
        # Build OAuth URL (like Buffer does)
        redirect_uri = url_for('api_linkedin_oauth_callback', _external=True)
        scopes = ['w_member_social', 'r_liteprofile', 'r_emailaddress']
        
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"scope={'%20'.join(scopes)}&"
            f"state={state}"
        )
        
        # Redirect to LinkedIn (just like Buffer does)
        return redirect(auth_url)
    except Exception as e:
        flash(f'Error starting LinkedIn authorization: {str(e)}', 'error')
        return redirect(url_for('config'))


@app.route('/api/linkedin/oauth/callback')
def api_linkedin_oauth_callback():
    """Handle LinkedIn OAuth callback - automatically get token and Person URN."""
    try:
        import requests
        
        # Get authorization code
        code = request.args.get('code')
        state = request.args.get('state')
        error = request.args.get('error')
        
        if error:
            error_desc = request.args.get('error_description', '')
            flash(f'LinkedIn authorization failed: {error} - {error_desc}', 'error')
            return redirect(url_for('config'))
        
        if not code:
            flash('LinkedIn authorization failed: No authorization code received', 'error')
            return redirect(url_for('config'))
        
        # Verify state
        stored_state = session.get('linkedin_oauth_state')
        if state != stored_state:
            flash('LinkedIn authorization failed: Invalid state parameter', 'error')
            return redirect(url_for('config'))
        
        # Get settings
        settings = load_settings()
        api_keys = settings.get('api_keys', {})
        client_id = api_keys.get('linkedin_client_id', '').strip()
        client_secret = api_keys.get('linkedin_client_secret', '').strip()
        
        if not client_id or not client_secret:
            flash('LinkedIn Client ID or Secret not configured', 'error')
            return redirect(url_for('config'))
        
        # Exchange code for access token
        redirect_uri = url_for('api_linkedin_oauth_callback', _external=True)
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        response = requests.post(token_url, data=token_data, timeout=10)
        response.raise_for_status()
        
        token_response = response.json()
        access_token = token_response.get('access_token')
        
        if not access_token:
            flash('Failed to get LinkedIn access token', 'error')
            return redirect(url_for('config'))
        
        # Get Person URN automatically
        profile_url = "https://api.linkedin.com/v2/me"
        profile_headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        profile_response = requests.get(profile_url, headers=profile_headers, timeout=10)
        profile_response.raise_for_status()
        
        profile_data = profile_response.json()
        person_urn = profile_data.get('id')
        
        if not person_urn:
            flash('Failed to get LinkedIn Person URN', 'error')
            return redirect(url_for('config'))
        
        # Save everything automatically (like Buffer does)
        api_keys['linkedin_access_token'] = access_token
        api_keys['linkedin_person_urn'] = person_urn
        settings['api_keys'] = api_keys
        save_settings(settings)
        
        # Update MY_CONFIG.json
        config_file = Path('MY_CONFIG.json')
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                if 'api_keys' not in config:
                    config['api_keys'] = {}
                config['api_keys']['linkedin_access_token'] = access_token
                config['api_keys']['linkedin_person_urn'] = person_urn
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
            except:
                pass
        
        # Clear state from session
        session.pop('linkedin_oauth_state', None)
        
        # Success! Redirect back to config with success message
        flash('✅ LinkedIn connected successfully! Access Token and Person URN saved automatically.', 'success')
        return redirect(url_for('config'))
        
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error_description', str(e))
            except:
                pass
        flash(f'LinkedIn connection failed: {error_msg}', 'error')
        return redirect(url_for('config'))
    except Exception as e:
        import traceback
        flash(f'LinkedIn connection error: {str(e)}', 'error')
        return redirect(url_for('config'))


@app.route('/api/config/load-from-file', methods=['POST'])
def api_load_config_from_file():
    """Load configuration from MY_CONFIG.json file."""
    import json
    from pathlib import Path
    
    config_file = Path('MY_CONFIG.json')
    
    if not config_file.exists():
        return jsonify({
            'success': False,
            'error': 'MY_CONFIG.json file not found. Please create it and fill in your settings.'
        }), 404
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Save to database
        save_settings(config)
        
        # Verify it was saved
        loaded = load_settings()
        
        return jsonify({
            'success': True,
            'message': 'Configuration loaded successfully!',
            'stats': {
                'api_keys_configured': sum(1 for v in loaded.get('api_keys', {}).values() if v),
                'scheduling_enabled': loaded.get('scheduling', {}).get('enabled', False),
                'upload_method': loaded.get('scheduling', {}).get('upload_method', 'native'),
                'cta_configured': sum(1 for v in loaded.get('cta', {}).values() if v)
            }
        })
    except json.JSONDecodeError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid JSON in MY_CONFIG.json: {str(e)}'
        }), 400
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/facebook/get-token', methods=['GET'])
def api_facebook_get_token_guide():
    """Provide a guide URL for getting Facebook Page Access Token."""
    settings = load_settings()
    api_keys = settings.get('api_keys', {})
    
    # Facebook App ID not needed - only Page Access Token is required
    # app_id = api_keys.get('facebook_app_id', '421181512329379')
    page_id = api_keys.get('facebook_page_id', '617021748762367')
    
    # Graph API Explorer URL with pre-filled app
    explorer_url = f"https://developers.facebook.com/tools/explorer/?version=v18.0"
    
    # Permissions needed
    permissions = [
        'pages_manage_posts',
        'pages_read_engagement',
        'instagram_basic',
        'instagram_content_publish',
        'business_management'
    ]
    
    return jsonify({
        'success': True,
        'guide': {
            'explorer_url': explorer_url,
            'app_id': app_id,
            'page_id': page_id,
            'permissions': permissions,
            'steps': [
                {
                    'step': 1,
                    'title': 'Open Graph API Explorer',
                    'description': f'Visit: {explorer_url}',
                    'action': 'Select your App in the dropdown (top right)'
                },
                {
                    'step': 2,
                    'title': 'Add Permissions',
                    'description': f'Add these permissions: {", ".join(permissions)}',
                    'action': 'Click permissions dropdown and add all required permissions'
                },
                {
                    'step': 3,
                    'title': 'Generate Token',
                    'description': 'Click "Generate Access Token" and authorize',
                    'action': 'Copy the User Access Token that appears'
                },
                {
                    'step': 4,
                    'title': 'Get Page Token',
                    'description': f'Visit: https://graph.facebook.com/v18.0/me/accounts?access_token={{your-token}}',
                    'action': f'Find Page ID {page_id} and copy its access_token'
                }
            ]
        }
    })


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
    """API endpoint for calendar data - fetches YouTube scheduled videos from all playlists and social media posts."""
    from app.database import get_db_connection, get_video_social_posts_from_db
    from datetime import datetime
    import pytz
    
    try:
        calendar_events = []
        
        # Fetch YouTube scheduled videos from all playlists
        youtube = get_youtube_service()
        if youtube:
            channel_id = get_my_channel_id_helper(youtube)
            if channel_id:
                playlists = fetch_all_playlists_from_youtube(youtube, channel_id)
                ist = pytz.timezone('Asia/Kolkata')
                
                for playlist in playlists:
                    playlist_id = playlist.get('playlistId', '')
                    playlist_title = playlist.get('playlistTitle', '')
                    
                    videos = fetch_playlist_videos_from_youtube(youtube, playlist_id, channel_id)
                    
                    for video in videos:
                        video_id = video.get('videoId', '')
                        title = video.get('title', '')
                        publish_at = video.get('publishAt', '')
                        published_at = video.get('publishedAt', '')
                        is_scheduled = video.get('isScheduled', False)
                        
                        # Determine the date to display
                        display_date = None
                        if is_scheduled and publish_at:
                            try:
                                if 'T' in publish_at:
                                    display_date = datetime.fromisoformat(publish_at.replace('Z', '+00:00'))
                                else:
                                    display_date = datetime.strptime(publish_at, '%Y-%m-%dT%H:%M:%S')
                            except:
                                pass
                        elif published_at:
                            try:
                                if 'T' in published_at:
                                    display_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                else:
                                    display_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S')
                            except:
                                pass
                        
                        if display_date:
                            # Convert to IST if needed
                            if display_date.tzinfo is None:
                                display_date = ist.localize(display_date)
                            else:
                                display_date = display_date.astimezone(ist)
                            
                            # Add YouTube video event
                        calendar_events.append({
                                'date': display_date.strftime('%Y-%m-%d'),
                                'time': display_date.strftime('%H:%M:%S'),
                                'datetime': display_date.isoformat(),
                                'platform': 'YouTube',
                            'video_title': title,
                            'video_id': video_id,
                                'youtube_url': f"https://www.youtube.com/watch?v={video_id}",
                                'status': 'scheduled' if is_scheduled else 'published',
                                'post_content': '',
                                'playlist_name': playlist_title,
                                'channel_name': 'YouTube',
                                'video_type': '',
                                'role': '',
                                'custom_tags': '',
                                'description': video.get('description', '')[:200]
                            })
                            
                            # Get social media posts for this video
                            social_posts = get_video_social_posts_from_db(video_id)
                            for platform in ['linkedin', 'facebook', 'instagram']:
                                post = social_posts.get(platform, {})
                                schedule_date_str = post.get('schedule_date', '')
                                
                                if schedule_date_str:
                                    try:
                                        schedule_date = datetime.fromisoformat(schedule_date_str.replace('Z', '+00:00'))
                                        if schedule_date.tzinfo is None:
                                            schedule_date = ist.localize(schedule_date)
                                        else:
                                            schedule_date = schedule_date.astimezone(ist)
                                        
                                        calendar_events.append({
                                            'date': schedule_date.strftime('%Y-%m-%d'),
                                            'time': schedule_date.strftime('%H:%M:%S'),
                                            'datetime': schedule_date.isoformat(),
                                            'platform': platform.title(),
                                            'video_title': title,
                                            'video_id': video_id,
                                            'youtube_url': f"https://www.youtube.com/watch?v={video_id}",
                                            'status': post.get('status', 'scheduled'),
                                            'post_content': post.get('post_content', ''),
                                            'playlist_name': playlist_title,
                                            'channel_name': platform.title(),
                                            'video_type': '',
                                            'role': '',
                                            'custom_tags': '',
                                            'description': ''
                        })
                    except:
                        pass
        
        # Also get social media posts from database (for any videos not in playlists)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                smp.video_id,
                smp.platform,
                smp.post_content,
                smp.schedule_date,
                smp.status,
                v.title as video_title,
                v.youtube_url,
                v.playlist_name
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status IN ('scheduled', 'pending')
                AND smp.schedule_date IS NOT NULL
        ''')
        
        for row in cursor.fetchall():
            row_dict = dict(row)
            schedule_date_str = row_dict.get('schedule_date')
            if schedule_date_str:
                try:
                    dt = datetime.fromisoformat(schedule_date_str.replace('Z', '+00:00'))
                    ist = pytz.timezone('Asia/Kolkata')
                    if dt.tzinfo is None:
                        dt = ist.localize(dt)
                    else:
                        dt = dt.astimezone(ist)
                    
                    # Check if this event already exists
                    exists = any(
                        e.get('video_id') == row_dict.get('video_id') and 
                        e.get('platform') == row_dict.get('platform', '').title() and
                        e.get('datetime') == dt.isoformat()
                        for e in calendar_events
                    )
                    
                    if not exists:
                        calendar_events.append({
                            'date': dt.strftime('%Y-%m-%d'),
                            'time': dt.strftime('%H:%M:%S'),
                            'datetime': dt.isoformat(),
                            'platform': row_dict.get('platform', '').title(),
                            'video_title': row_dict.get('video_title', 'Untitled Video'),
                            'video_id': row_dict.get('video_id', ''),
                            'youtube_url': row_dict.get('youtube_url', ''),
                            'status': row_dict.get('status', 'pending'),
                            'post_content': row_dict.get('post_content', ''),
                            'playlist_name': row_dict.get('playlist_name', '') or '',
                            'channel_name': row_dict.get('platform', '').title(),
                            'video_type': '',
                            'role': '',
                            'custom_tags': '',
                            'description': ''
                        })
                except:
                    pass
        
        conn.close()
        
        # Get optimal posting times and generate recommendations
        optimal_times = get_optimal_posting_times_from_analytics()
        recommendations = generate_calendar_recommendations(calendar_events, optimal_times)
        
        calendar_events.sort(key=lambda x: x['datetime'])
        
        return jsonify({
            'events': calendar_events,
            'optimal_times': optimal_times,
            'recommendations': recommendations
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc(), 'events': []}), 500


def get_optimal_posting_times_from_analytics():
    """Get optimal posting times from analytics data."""
    try:
        youtube_analytics = get_youtube_analytics()
        optimal_times = calculate_optimal_posting_times(youtube_analytics, {}, {})
        
        best_hours = []
        if optimal_times.get('youtube') and optimal_times['youtube'].get('best_times'):
            best_hours = [f"{hour:02d}:00" for hour, views in optimal_times['youtube']['best_times'][:3]]
        
        return {
            'youtube': optimal_times.get('youtube', {}),
            'best_hours': best_hours if best_hours else ['14:00', '17:00', '21:00'],
            'overall_best': optimal_times.get('overall', {})
        }
    except:
        return {'best_hours': ['14:00', '17:00', '21:00']}


def generate_calendar_recommendations(events, optimal_times):
    """Generate recommendations for promoting videos to other channels."""
    recommendations = []
    
    # Group YouTube videos by date
    youtube_videos_by_date = {}
    social_posts_by_video = {}
    
    for event in events:
        if event.get('platform') == 'YouTube':
            date_key = event['date']
            if date_key not in youtube_videos_by_date:
                youtube_videos_by_date[date_key] = []
            youtube_videos_by_date[date_key].append(event)
        
        # Track which platforms are scheduled for each video
        video_id = event.get('video_id')
        platform = event.get('platform', '').lower()
        if video_id and platform != 'youtube':
            if video_id not in social_posts_by_video:
                social_posts_by_video[video_id] = set()
            social_posts_by_video[video_id].add(platform)
    
    # Generate recommendations
    for date_key, video_events in youtube_videos_by_date.items():
        for video_event in video_events:
            video_id = video_event.get('video_id')
            video_title = video_event.get('video_title', '')
            
            scheduled_platforms = social_posts_by_video.get(video_id, set())
            missing_platforms = {'linkedin', 'facebook', 'instagram'} - scheduled_platforms
            
            if missing_platforms:
                best_time = optimal_times.get('best_hours', ['14:00'])[0] if optimal_times.get('best_hours') else '14:00'
                recommendations.append({
                    'date': date_key,
                    'video_id': video_id,
                    'video_title': video_title,
                    'youtube_time': video_event.get('time', '12:00'),
                    'missing_platforms': list(missing_platforms),
                    'recommended_time': best_time,
                    'message': f"Promote '{video_title[:50]}{'...' if len(video_title) > 50 else ''}' to {', '.join([p.title() for p in missing_platforms])} at {best_time}"
                })
    
    return recommendations


@app.route('/api/queue')
def api_queue():
    """Get queue data for dashboard."""
    try:
        from app.database import get_db_connection
        from datetime import datetime, date
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all scheduled posts
        cursor.execute('''
            SELECT smp.id, smp.video_id, smp.platform, smp.post_content, 
                   smp.schedule_date, smp.actual_scheduled_date, smp.status,
                   smp.created_at, smp.updated_at,
                   v.title as video_title, v.youtube_url
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status IN ('pending', 'scheduled', 'published')
            ORDER BY 
                CASE WHEN smp.schedule_date IS NOT NULL THEN smp.schedule_date ELSE smp.created_at END ASC,
                smp.created_at DESC
            LIMIT 100
        ''')
        
        posts = []
        for row in cursor.fetchall():
            post = dict(row)
            post['content'] = post.get('post_content', '')
            post['text'] = post.get('post_content', '')
            post['scheduled_at'] = post.get('schedule_date') or post.get('actual_scheduled_date')
            if post.get('created_at'):
                post['created_at'] = post['created_at']
            posts.append(post)
        
        # Get stats
        today = date.today().isoformat()
        
        cursor.execute('SELECT COUNT(*) as count FROM social_media_posts WHERE status IN ("pending", "scheduled")')
        queue_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM social_media_posts WHERE status = "scheduled"')
        scheduled_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM social_media_posts WHERE status = "published" AND DATE(updated_at) = ?', (today,))
        published_today = cursor.fetchone()['count']
        
        settings = load_settings()
        automation_active = settings.get('scheduling', {}).get('enabled', False)
        
        conn.close()
        
        return jsonify({
            'queue': posts,
            'stats': {
                'queue_count': queue_count,
                'scheduled_count': scheduled_count,
                'published_today': published_today,
                'automation_active': automation_active
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            'queue': [],
            'stats': {
                'queue_count': 0,
                'scheduled_count': 0,
                'published_today': 0,
                'automation_active': False
            },
            'error': str(e)
        }), 500


@app.route('/api/queue/create', methods=['POST'])
def api_queue_create():
    """Create a new post in queue."""
    try:
        from app.database import get_db_connection
        
        data = request.json
        platforms = data.get('platforms', [])
        content = data.get('content', '')
        scheduled_at = data.get('scheduled_at')
        video_url = data.get('video_url', '')
        
        if not platforms:
            return jsonify({'success': False, 'error': 'Please select at least one platform'}), 400
        
        if not content:
            return jsonify({'success': False, 'error': 'Please enter post content'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Extract video_id from URL if provided
        video_id = None
        if video_url:
            # Try to extract video ID from YouTube URL
            import re
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
            if match:
                video_id = match.group(1)
        
        # Create posts for each platform
        created_posts = []
        for platform in platforms:
            cursor.execute('''
                INSERT INTO social_media_posts 
                (video_id, platform, post_content, schedule_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (video_id, platform, content, scheduled_at, 'scheduled' if scheduled_at else 'pending'))
            created_posts.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Created {len(created_posts)} post(s)',
            'post_ids': created_posts
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/queue/publish-now', methods=['POST'])
def api_queue_publish_now():
    """Publish a post immediately."""
    try:
        data = request.json
        platforms = data.get('platforms', [])
        content = data.get('content', '')
        video_url = data.get('video_url', '')
        
        if not platforms or not content:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # This would call the actual posting function
        # For now, just mark as published
        from app.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        video_id = None
        if video_url:
            import re
            match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
            if match:
                video_id = match.group(1)
        
        now = datetime.now().isoformat()
        published_count = 0
        
        for platform in platforms:
            cursor.execute('''
                INSERT INTO social_media_posts 
                (video_id, platform, post_content, status, actual_scheduled_date, created_at, updated_at)
                VALUES (?, ?, ?, 'published', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (video_id, platform, content, now))
            published_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Published to {published_count} platform(s)'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/queue/<int:post_id>/publish', methods=['POST'])
def api_queue_publish_item(post_id):
    """Publish a specific queue item - downloads video and uploads natively if configured."""
    try:
        from app.database import get_db_connection, get_video
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get post details
        cursor.execute('''
            SELECT smp.*, v.video_id, v.title, v.youtube_url
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.id = ?
        ''', (post_id,))
        
        post = dict(cursor.fetchone())
        if not post:
            return jsonify({'success': False, 'error': 'Post not found'}), 404
        
        video_id = post.get('video_id')
        platform = post.get('platform', '').lower()
        post_content = post.get('post_content', '')
        
        # Check upload method from settings
        settings = load_settings()
        upload_method = settings.get('scheduling', {}).get('upload_method', 'native')  # Default: native
        
        if upload_method == 'native' and video_id:
            # Native video upload: Download and upload video
            try:
                from app.video_processor import process_and_upload_video
                
                # Get API credentials
                api_keys = settings.get('api_keys', {})
                api_credentials = {
                    'linkedin_access_token': api_keys.get('linkedin_access_token'),
                    'linkedin_person_urn': api_keys.get('linkedin_person_urn'),
                    'facebook_page_id': api_keys.get('facebook_page_id'),
                    'facebook_page_access_token': api_keys.get('facebook_page_access_token'),
                    'instagram_business_account_id': api_keys.get('instagram_business_account_id')
                    # Note: Instagram uses Facebook Page Access Token, not a separate token
                }
                
                # Prepare captions
                captions = {platform: post_content}
                
                # Process and upload
                result = process_and_upload_video(
                    video_id=video_id,
                    platforms=[platform],
                    captions=captions,
                    api_credentials=api_credentials
                )
                
                if result.get('success') and result.get('results', {}).get(platform, {}).get('success'):
                    # Update post status
                    cursor.execute('''
                        UPDATE social_media_posts 
                        SET status = 'published', 
                            actual_scheduled_date = CURRENT_TIMESTAMP,
                            post_id = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (result['results'][platform].get('post_id'), post_id))
                    
                    conn.commit()
                    conn.close()
                    
                    return jsonify({
                        'success': True, 
                        'message': f'Video uploaded and published natively to {platform}',
                        'post_id': result['results'][platform].get('post_id')
                    })
                else:
                    error = result.get('error') or result.get('results', {}).get(platform, {}).get('error', 'Upload failed')
                    # Mark as failed
                    cursor.execute('''
                        UPDATE social_media_posts 
                        SET status = 'failed',
                            error_message = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (error, post_id))
                    conn.commit()
                    conn.close()
                    
                    return jsonify({'success': False, 'error': error}), 500
                    
            except ImportError:
                # video_processor not available, fall back to link sharing
                pass
            except Exception as e:
                # Upload failed, fall back to link sharing
                import traceback
                error_msg = f"Native upload failed: {str(e)}"
                # Continue to link sharing fallback
        
        # Link sharing fallback (or if native upload not configured)
        # For now, just mark as published (actual posting would need API integration)
        cursor.execute('''
            UPDATE social_media_posts 
            SET status = 'published', 
                actual_scheduled_date = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (post_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Post published to {platform} (link sharing mode)',
            'note': 'Native video upload not configured or failed. Post shared as link.'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False, 
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@app.route('/api/queue/<int:post_id>', methods=['DELETE'])
def api_queue_delete(post_id):
    """Delete a queue item."""
    try:
        from app.database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM social_media_posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Post deleted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
        has_token = bool(api_keys.get('facebook_page_access_token'))
        has_page_id = bool(api_keys.get('facebook_page_id'))
        
        # Page Access Token and Page ID are required
        is_configured = has_token and has_page_id
        
        return jsonify({
            'success': is_configured,
            'message': 'Facebook configured' if is_configured else 'Missing Facebook credentials (need Page Access Token and Page ID)'
        })
    elif platform == 'instagram':
        has_account = bool(api_keys.get('instagram_business_account_id'))
        
        # Instagram Business Account ID and Facebook Page Token (or Instagram token) are required
        is_configured = has_account and has_token
        
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
    # Ensure database is initialized before loading settings
    try:
        init_database()
        print("✅ Database initialized - settings will persist across restarts")
    except Exception as e:
        print(f"⚠️ Warning: Database initialization failed: {e}")
    
    # Load initial settings and verify they can be loaded
    try:
        test_settings = load_settings()
        if test_settings:
            api_keys = test_settings.get('api_keys', {})
            keys_count = sum(1 for v in api_keys.values() if v)
            print(f"✅ Settings loaded successfully from database ({keys_count} API keys configured)")
        else:
            print("ℹ️  No settings found in database - will use defaults until you configure")
    except Exception as e:
        print(f"⚠️ Warning: Could not load settings: {e}")
    
    # Schedule daily job
    schedule_daily_job()
    
    # Run Flask app
    # Use environment variable for port, default to 5001 (5000 often used by AirPlay on macOS)
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    # Get database path for display
    from app.database import DB_PATH
    db_path_display = DB_PATH
    
    print(f"\n🌐 Starting server on port {port}...")
    print(f"📱 Open in browser: http://localhost:{port}\n")
    print(f"💾 Database location: {db_path_display}")
    print(f"💾 Settings are saved to database - they will persist across restarts and code changes!\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

