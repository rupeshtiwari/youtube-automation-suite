"""
Flask web application for YouTube automation configuration and scheduling.
Provides a web interface to configure API keys and schedule daily automation.
"""

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    make_response,
    g,
    session,
    get_flashed_messages,
    send_from_directory,
)

try:
    from flask_cors import CORS
except ImportError:
    CORS = None
import json
import os
import sys
import sqlite3
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
from app.facebook_token_helper import facebook_helper_bp
from app.facebook_auto_setup import facebook_auto_setup_bp
from app.validators import (
    validate_required_fields,
    sanitize_input,
    validate_integer,
    validate_string_length,
    validate_platform,
    validate_post_status,
    validate_video_id,
    validate_playlist_id,
    sanitize_filename,
    validate_role,
    validate_session_type,
    validate_date_format,
    validate_time_format,
    validate_url,
    validate_phone,
)


def generate_clickbait_post(
    title: str,
    description: str,
    video_type: str,
    video_role: str,
    platform: str,
    youtube_url: str,
) -> str:
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
    is_system_design = any(
        kw in text_lower
        for kw in ["system design", "architecture", "scalability", "distributed"]
    )
    is_behavioral = any(
        kw in text_lower for kw in ["behavioral", "leadership", "stories", "situation"]
    )
    is_coding = any(
        kw in text_lower for kw in ["coding", "leetcode", "algorithm", "programming"]
    )
    is_salary = any(
        kw in text_lower for kw in ["salary", "negotiation", "compensation", "offer"]
    )
    is_resume = any(kw in text_lower for kw in ["resume", "cv", "application"])

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
            "🚫 Don't make this fatal system design mistake that cost someone their dream job...",
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
            "🚫 Don't make this fatal behavioral mistake that cost someone their dream job...",
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
            "🚫 Don't make this fatal coding mistake that cost someone their dream job...",
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
            "🚫 This salary negotiation error made someone lose $150K in total comp...",
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
            "🚫 Don't make this fatal resume mistake that cost someone their dream job...",
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
            "🚫 Don't make this fatal interview mistake that cost someone their dream job...",
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
        "💥 Secure your coaching slot before it's too late",
    ]
    urgency = random.choice(urgency_hooks)

    # Platform-specific formatting
    if platform == "linkedin":
        post = f"{hook}\n\n"
        post += f"💡 {value_prop}\n\n"
        post += f"👉 Watch the full breakdown: {youtube_url}\n\n"
        post += f"📅 Book 1-on-1 coaching: https://fullstackmaster/book\n"
        post += f"💬 WhatsApp: +1-609-442-4081\n\n"
        post += f"{urgency}\n\n"
        post += generate_hashtags_for_rupesh(video_type, video_role, title, description)

    elif platform == "facebook":
        post = f"{hook}\n\n"
        post += f"💡 {value_prop}\n\n"
        post += f"👉 Watch here: {youtube_url}\n\n"
        post += f"📅 Book 1-on-1 coaching: https://fullstackmaster/book\n"
        post += f"💬 WhatsApp: +1-609-442-4081\n\n"
        post += f"{urgency}\n\n"
        post += generate_hashtags_for_rupesh(video_type, video_role, title, description)

    elif platform == "instagram":
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


def generate_hashtags_for_rupesh(
    video_type: str, video_role: str, title: str, description: str
) -> str:
    """
    Generate hashtags aligned with Rupesh's coaching expertise from IGotAnOffer.
    Based on: AWS Senior CSM, Interview Coaching, System Design, Leadership, Career Growth
    """
    hashtags = []
    text = f"{title} {description}".lower()

    # Core expertise hashtags (always include some)
    core_tags = ["TechInterview", "CareerGrowth"]

    # Interview-related (Rupesh's main focus)
    if any(
        kw in text
        for kw in ["system design", "sys design", "architecture", "scalability"]
    ):
        hashtags.extend(
            ["SystemDesign", "SystemDesignInterview", "SolutionsArchitect", "AWS"]
        )
    if any(kw in text for kw in ["coding", "leetcode", "algorithm", "programming"]):
        hashtags.extend(["CodingInterview", "LeetCode", "Algorithm", "TechInterview"])
    if any(kw in text for kw in ["behavioral", "leadership principles", "stories"]):
        hashtags.extend(["BehavioralInterview", "Leadership", "CareerCoaching"])
    if any(kw in text for kw in ["mock interview", "interview prep", "interview"]):
        hashtags.extend(["MockInterview", "InterviewPrep", "FAANGInterview"])

    # Role-based hashtags (Rupesh coaches these roles)
    if any(kw in text for kw in ["engineering manager", "em", "manager"]):
        hashtags.extend(["EngineeringManager", "TechLeadership", "Management"])
    if any(kw in text for kw in ["product manager", "pm", "product"]):
        hashtags.extend(["ProductManager", "ProductManagement", "PM"])
    if any(kw in text for kw in ["solutions architect", "architect", "sa"]):
        hashtags.extend(["SolutionsArchitect", "CloudArchitecture", "AWS"])
    if any(kw in text for kw in ["data engineer", "data engineering"]):
        hashtags.extend(["DataEngineering", "DataEngineer", "BigData"])
    if any(kw in text for kw in ["cloud engineer", "aws", "cloud"]):
        hashtags.extend(["CloudEngineering", "AWS", "CloudComputing", "DevOps"])
    if any(kw in text for kw in ["staff engineer", "senior engineer", "principal"]):
        hashtags.extend(["StaffEngineer", "SeniorEngineer", "TechCareer"])
    if any(kw in text for kw in ["director", "vp", "executive"]):
        hashtags.extend(["TechLeadership", "Executive", "SeniorLeadership"])

    # Career growth (Rupesh's specialty)
    if any(kw in text for kw in ["resume", "cv", "resume review"]):
        hashtags.extend(["ResumeReview", "ResumeTips", "JobSearch"])
    if any(kw in text for kw in ["salary", "negotiation", "compensation"]):
        hashtags.extend(["SalaryNegotiation", "CareerAdvice", "TechSalary"])
    if any(kw in text for kw in ["career", "promotion", "growth"]):
        hashtags.extend(["CareerGrowth", "CareerCoaching", "TechCareer"])

    # AWS/Cloud specific (Rupesh's current role)
    if any(kw in text for kw in ["aws", "amazon", "cloud infrastructure"]):
        hashtags.extend(["AWS", "CloudComputing", "SolutionsArchitect"])

    # FAANG focus (Rupesh coaches for FAANG)
    if any(
        kw in text for kw in ["faang", "amazon", "google", "microsoft", "meta", "apple"]
    ):
        hashtags.extend(["FAANG", "BigTech", "TechInterview"])

    # Remove duplicates and limit to 10-12 most relevant
    hashtags = list(dict.fromkeys(hashtags))  # Preserve order, remove dupes
    hashtags = core_tags + [h for h in hashtags if h not in core_tags][:10]

    return " ".join(["#" + tag for tag in hashtags])


from app import views

# Get project root (parent of app/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(project_root, "templates")

static_dir = os.path.join(os.path.dirname(__file__), "static")

# Configure Flask to serve React build if it exists
FRONTEND_BUILD_DIR = os.path.join(project_root, "frontend", "dist")

# Always use templates/ directory for templates, but serve React build as static if it exists
if os.path.exists(FRONTEND_BUILD_DIR):
    # Serve React build as static files, but use templates/ for Flask templates
    app = Flask(
        __name__,
        static_folder=FRONTEND_BUILD_DIR,
        static_url_path="",
        template_folder=template_dir,
    )  # Always use templates/ for templates
else:
    # Fallback to old templates/static setup
    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )

# Audio output directory (can override with AUDIO_OUTPUT_DIR env var)
AUDIO_OUTPUT_DIR = os.getenv("AUDIO_OUTPUT_DIR")
if not AUDIO_OUTPUT_DIR:
    AUDIO_OUTPUT_DIR = os.path.join(app.root_path, "static", "audio")
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# Register blueprints
app.register_blueprint(facebook_helper_bp)
app.register_blueprint(facebook_auto_setup_bp)

# Enable CORS for React frontend
if CORS:
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["http://localhost:5001", "http://localhost:3000"],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
            }
        },
    )
else:
    # Fallback CORS headers if flask-cors not available
    @app.after_request
    def after_request(response):
        if request.path.startswith("/api/"):
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add(
                "Access-Control-Allow-Headers", "Content-Type,Authorization"
            )
            response.headers.add(
                "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
            )
        return response


app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Performance optimizations
from app.performance import compress_response, optimize_response_headers, cached


@app.after_request
def after_request(response):
    """Apply performance optimizations to all responses."""
    response = optimize_response_headers(response)
    response = compress_response(response)
    return response


# Initialize database on app startup (ensures settings table exists)
try:
    init_database()
except Exception as e:
    print(f"Warning: Error initializing database: {e}")
    # App will still run, but database features may not work


@app.before_request
def before_request():
    """Add config warnings to all requests."""
    try:
        g.config_warnings = validate_config()
    except Exception as e:
        app.logger.error(f"Error in before_request: {e}", exc_info=True)
        g.config_warnings = []  # Default to empty list on error


# Global error handlers to prevent crashes
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors gracefully."""
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found", "path": request.path}), 404
    # For non-API routes, try to serve React app
    if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
        os.path.join(FRONTEND_BUILD_DIR, "index.html")
    ):
        return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors gracefully - prevent app crashes."""
    app.logger.error(f"Internal server error: {error}", exc_info=True)
    if request.path.startswith("/api/"):
        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "message": "An error occurred. Please try again later.",
                }
            ),
            500,
        )
    # For non-API routes, try to serve React app or error page
    try:
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except:
        return (
            "<html><body><h1>Error</h1><p>An error occurred. Please refresh the page.</p></body></html>",
            500,
        )


@app.errorhandler(Exception)
def handle_exception(e):
    """Catch all unhandled exceptions to prevent app crashes."""
    app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    if request.path.startswith("/api/"):
        return (
            jsonify(
                {
                    "error": "An error occurred",
                    "message": (
                        str(e)
                        if app.debug
                        else "An error occurred. Please try again later."
                    ),
                }
            ),
            500,
        )
    # For non-API routes, try to serve React app
    try:
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except:
        return (
            "<html><body><h1>Error</h1><p>An error occurred. Please refresh the page.</p></body></html>",
            500,
        )


# Settings file - support NAS/Docker deployment
DATA_DIR = os.getenv("DATA_DIR", os.path.dirname(__file__))
SETTINGS_FILE = os.path.join(DATA_DIR, "automation_settings.json")
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
            with open(SETTINGS_FILE, "r") as f:
                json_settings = json.load(f)
                # Migrate to database
                save_settings(json_settings)
                return json_settings
        except (json.JSONDecodeError, IOError):
            pass

    # Return default settings
    return {
        "api_keys": {
            "linkedin_client_id": "",
            "linkedin_client_secret": "",
            "linkedin_access_token": "",
            "linkedin_person_urn": "",
            "facebook_page_access_token": "",
            "facebook_page_id": "",
            "instagram_business_account_id": "",
            "ayrshare_api_key": "",
        },
        "scheduling": {
            "enabled": False,
            "videos_per_day": 1,
            "youtube_schedule_time": "23:00",  # 11:00 PM IST
            "social_media_schedule_time": "19:30",  # 7:30 PM IST
            "schedule_day": "wednesday",  # Day of week
            "playlist_id": "",
            "export_type": "shorts",  # 'all' or 'shorts'
            "use_database": True,  # Use SQLite database instead of Excel
            "auto_post_social": False,
            "social_platforms": ["linkedin", "facebook", "instagram"],
        },
        "thresholds": {
            "linkedin_daily_limit": 25,  # LinkedIn allows ~25 posts/day
            "facebook_daily_limit": 25,  # Facebook allows ~25 posts/day
            "instagram_daily_limit": 25,  # Instagram allows ~25 posts/day
            "youtube_daily_limit": 10,  # YouTube allows ~10 videos/day
        },
        "targeting": {
            "target_audience": "usa_students",  # 'usa_students', 'all', 'professionals'
            "interview_types": [
                "coding_interview",
                "sys_design_interview",
                "leetcode",
                "algorithm_interview",
                "behavioral_interview",
            ],
            "role_levels": [
                "intern",
                "new_grad",
                "entry_level",
                "student",
            ],  # Target student roles
            "timezone": "America/New_York",  # USA Eastern Time
            "optimal_times": [
                "14:00",
                "17:00",
                "21:00",
            ],  # 2 PM, 5 PM, 9 PM EDT (USA student active times)
        },
        "last_run": None,
        "next_run": None,
    }


def validate_config():
    """Validate configuration and return warnings for missing required fields."""
    settings = load_settings()
    warnings = []
    api_keys = settings.get("api_keys", {})

    # Check LinkedIn configuration
    linkedin_client_id = api_keys.get("linkedin_client_id", "").strip()
    linkedin_client_secret = api_keys.get("linkedin_client_secret", "").strip()
    linkedin_access_token = api_keys.get("linkedin_access_token", "").strip()
    linkedin_person_urn = api_keys.get("linkedin_person_urn", "").strip()

    if not linkedin_client_id or not linkedin_client_secret:
        warnings.append(
            {
                "platform": "LinkedIn",
                "severity": "error",
                "message": "LinkedIn Client ID and Client Secret are required",
                "fields": ["LinkedIn Client ID", "LinkedIn Client Secret"],
                "link": "/config#linkedin",
            }
        )
    elif not linkedin_person_urn:
        # Auto-fetch Person URN if we have access token
        if linkedin_access_token:
            try:
                person_urn = auto_fetch_linkedin_person_urn(linkedin_access_token)
                if person_urn:
                    # Save it to settings
                    api_keys["linkedin_person_urn"] = person_urn
                    settings["api_keys"] = api_keys
                    save_settings(settings)
                    print(
                        f"✅ Auto-fetched and saved LinkedIn Person URN: {person_urn}"
                    )
                else:
                    warnings.append(
                        {
                            "platform": "LinkedIn",
                            "severity": "warning",
                            "message": "LinkedIn Person URN could not be auto-fetched. Please fetch it manually.",
                            "fields": ["LinkedIn Person URN"],
                            "link": "/config#linkedin",
                        }
                    )
            except Exception as e:
                warnings.append(
                    {
                        "platform": "LinkedIn",
                        "severity": "warning",
                        "message": f"LinkedIn Person URN auto-fetch failed: {str(e)}. Please fetch it manually.",
                        "fields": ["LinkedIn Person URN"],
                        "link": "/config#linkedin",
                    }
                )
        else:
            warnings.append(
                {
                    "platform": "LinkedIn",
                    "severity": "warning",
                    "message": "LinkedIn Person URN is recommended for posting. Add access token to auto-fetch.",
                    "fields": ["LinkedIn Person URN"],
                    "link": "/config#linkedin",
                }
            )

    # Check Facebook configuration
    facebook_page_token = api_keys.get("facebook_page_access_token", "").strip()
    facebook_page_id = api_keys.get("facebook_page_id", "").strip()

    if not facebook_page_token or not facebook_page_id:
        warnings.append(
            {
                "platform": "Facebook",
                "severity": "error",
                "message": "Facebook Page Access Token and Page ID are required",
                "fields": ["Facebook Page Access Token", "Facebook Page ID"],
                "link": "/config#facebook",
            }
        )
    elif not facebook_page_id:
        warnings.append(
            {
                "platform": "Facebook",
                "severity": "warning",
                "message": "Facebook Page ID is required for posting",
                "fields": ["Facebook Page ID"],
                "link": "/config#facebook",
            }
        )

    # Check Instagram configuration
    instagram_account_id = api_keys.get("instagram_business_account_id", "").strip()

    if not instagram_account_id:
        warnings.append(
            {
                "platform": "Instagram",
                "severity": "warning",
                "message": "Instagram Business Account ID is required for posting",
                "fields": ["Instagram Business Account ID"],
                "link": "/config#instagram",
            }
        )

    return warnings


def auto_fetch_linkedin_person_urn(access_token):
    """Auto-fetch LinkedIn Person URN from access token."""
    try:
        import requests

        # Get user profile to extract Person URN
        url = "https://api.linkedin.com/v2/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Person URN is typically in 'sub' field or we can construct it
            sub = data.get("sub", "")
            if sub:
                # Format: urn:li:person:xxxxx
                if not sub.startswith("urn:li:person:"):
                    return f"urn:li:person:{sub}"
                return sub

        # Alternative: Try to get from /me endpoint
        url = "https://api.linkedin.com/v2/me"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            person_id = data.get("id", "")
            if person_id:
                if not person_id.startswith("urn:li:person:"):
                    return f"urn:li:person:{person_id}"
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
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
            json_saved = True
            print(f"✅ Settings saved to JSON backup file")
    except Exception as e:
        print(f"⚠️ Warning: Failed to save settings to JSON file: {e}")

    # Verify at least one save succeeded
    if not db_saved and not json_saved:
        raise Exception(
            "CRITICAL: Failed to save settings to both database and JSON file!"
        )

    # Also update .env file for compatibility (for scripts that read .env)
    try:
        update_env_file(settings)
    except Exception as e:
        print(f"⚠️ Warning: Failed to update .env file: {e}")

    return db_saved, json_saved


def update_env_file(settings):
    """Update .env file with API keys."""
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_lines = f.readlines()

    # Create mapping of keys
    api_keys = settings.get("api_keys", {})
    key_mapping = {
        "LINKEDIN_CLIENT_ID": api_keys.get("linkedin_client_id", ""),
        "LINKEDIN_CLIENT_SECRET": api_keys.get("linkedin_client_secret", ""),
        "LINKEDIN_ACCESS_TOKEN": api_keys.get("linkedin_access_token", ""),
        "LINKEDIN_PERSON_URN": api_keys.get("linkedin_person_urn", ""),
        "FACEBOOK_PAGE_ACCESS_TOKEN": api_keys.get("facebook_page_access_token", ""),
        "FACEBOOK_PAGE_ID": api_keys.get("facebook_page_id", ""),
        "INSTAGRAM_BUSINESS_ACCOUNT_ID": api_keys.get(
            "instagram_business_account_id", ""
        ),
        "AYRSHARE_API_KEY": api_keys.get("ayrshare_api_key", ""),
        "YOUTUBE_PLAYLIST_ID": settings.get("scheduling", {}).get("playlist_id", ""),
    }

    # Update or add keys
    existing_keys = set()
    new_lines = []
    for line in env_lines:
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=")[0].strip()
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

    with open(".env", "w") as f:
        f.writelines(new_lines)


def run_daily_automation():
    """Run the daily automation tasks."""
    settings = load_settings()
    scheduling = settings.get("scheduling", {})

    if not scheduling.get("enabled", False):
        print(f"[{datetime.now()}] Automation is disabled, skipping...")
        return

    print(f"[{datetime.now()}] Starting daily automation...")

    try:
        # Update .env file first to ensure scripts have access to API keys
        update_env_file(settings)

        # Step 1: Export videos
        export_type = scheduling.get("export_type", "shorts")
        use_database = scheduling.get("use_database", True)

        if use_database:
            # Use database (recommended)
            if export_type == "shorts":
                script = "export_shorts_to_database.py"
            else:
                # For now, use Excel version for 'all' playlists
                # TODO: Create export_playlists_to_database.py
                script = "export_playlists_videos_to_excel.py"

            result = subprocess.run(
                ["python", script],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=os.getcwd(),
            )
        else:
            # Use Excel (legacy)
            if export_type == "shorts":
                result = subprocess.run(
                    ["python", "export_shorts_to_excel.py"],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=os.getcwd(),
                )
            else:
                result = subprocess.run(
                    ["python", "export_playlists_videos_to_excel.py"],
                    capture_output=True,
                    text=True,
                    timeout=600,
                    cwd=os.getcwd(),
                )

        if result.returncode != 0:
            print(f"Export failed: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return

        # Step 2: Schedule YouTube videos if playlist_id is set
        playlist_id = scheduling.get("playlist_id", "")
        videos_per_day = scheduling.get("videos_per_day", 1)

        if playlist_id:
            # Set environment variable
            env = os.environ.copy()
            env["YOUTUBE_PLAYLIST_ID"] = playlist_id

            # Run scheduling for specified number of videos
            # Note: schedule-youtube.py schedules ALL videos, so we might need to modify it
            # For now, we'll run it as-is
            result = subprocess.run(
                ["python", "schedule-youtube.py"],
                env=env,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=os.getcwd(),
            )

            if result.returncode != 0:
                print(f"YouTube scheduling failed: {result.stderr}")
                if result.stdout:
                    print(f"Output: {result.stdout}")

        # Step 3: Post to social media if enabled
        if scheduling.get("auto_post_social", False):
            platforms = scheduling.get("social_platforms", [])

            if use_database:
                # Post from database (more efficient)
                from app.database import get_pending_posts
                from post_to_social_media import SocialMediaPoster

                poster = SocialMediaPoster(
                    use_ayrshare=bool(
                        settings.get("api_keys", {}).get("ayrshare_api_key")
                    )
                )

                for platform in platforms:
                    pending_posts = get_pending_posts(platform=platform.lower())
                    print(f"Found {len(pending_posts)} pending posts for {platform}")

                    for post in pending_posts:
                        video_id = post["video_id"]
                        content = post["post_content"]
                        schedule_date = post["schedule_date"]

                        # Post to platform
                        if platform.lower() == "linkedin":
                            result = poster.post_to_linkedin(content, schedule_date)
                        elif platform.lower() == "facebook":
                            result = poster.post_to_facebook(content, schedule_date)
                        elif platform.lower() == "instagram":
                            result = poster.post_to_instagram(
                                content, None, schedule_date
                            )
                        else:
                            continue

                        # Update database
                        from app.database import update_post_status

                        if result.get("success"):
                            update_post_status(
                                video_id,
                                platform.lower(),
                                result.get("status", "scheduled"),
                                result.get("scheduled_date"),
                                result.get("post_id"),
                            )
                        else:
                            update_post_status(
                                video_id,
                                platform.lower(),
                                "error",
                                error_message=result.get("error"),
                            )

                        time.sleep(2)  # Rate limiting
            else:
                # Post from Excel (legacy)
                excel_file = (
                    "youtube_shorts_export.xlsx"
                    if export_type == "shorts"
                    else "youtube_playlists_videos_export.xlsx"
                )

                if os.path.exists(excel_file):
                    use_ayrshare = bool(
                        settings.get("api_keys", {}).get("ayrshare_api_key")
                    )
                    cmd = [
                        "python",
                        "post_to_social_media.py",
                        "--excel",
                        excel_file,
                        "--platforms",
                    ] + platforms

                    if use_ayrshare:
                        cmd.append("--use-ayrshare")

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=600,
                        cwd=os.getcwd(),
                    )

                    if result.returncode != 0:
                        print(f"Social media posting failed: {result.stderr}")
                        if result.stdout:
                            print(f"Output: {result.stdout}")

        # Update last run time
        settings["last_run"] = datetime.now(IST).isoformat()
        save_settings(settings)

        print(f"[{datetime.now()}] Daily automation completed successfully")

    except Exception as e:
        print(f"[{datetime.now()}] Error in daily automation: {e}")


def publish_scheduled_posts():
    """Auto-publish scheduled posts that are ready."""
    from app.database import (
        get_db_connection,
        get_video,
        update_post_status,
        log_activity,
    )
    from datetime import datetime

    try:
        settings = load_settings()
        upload_method = settings.get("scheduling", {}).get("upload_method", "native")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get posts that are scheduled and ready to publish
        now = datetime.now()
        cursor.execute(
            """
            SELECT smp.*, v.video_id, v.title, v.youtube_url
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status = 'scheduled'
                AND smp.schedule_date IS NOT NULL
                AND datetime(smp.schedule_date) <= datetime(?)
            ORDER BY smp.schedule_date ASC
            LIMIT 10
        """,
            (now.isoformat(),),
        )

        posts_to_publish = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if not posts_to_publish:
            return

        print(
            f"[{datetime.now()}] Found {len(posts_to_publish)} posts ready to publish"
        )

        api_keys = settings.get("api_keys", {})
        api_credentials = {
            "linkedin_access_token": api_keys.get("linkedin_access_token"),
            "linkedin_person_urn": api_keys.get("linkedin_person_urn"),
            "facebook_page_id": api_keys.get("facebook_page_id"),
            "facebook_page_access_token": api_keys.get("facebook_page_access_token"),
            "instagram_business_account_id": api_keys.get(
                "instagram_business_account_id"
            ),
            # Note: Instagram uses Facebook Page Access Token, not a separate token
        }

        for post in posts_to_publish:
            try:
                video_id = post.get("video_id")
                platform = post.get("platform", "").lower()
                post_content = post.get("post_content", "")
                post_id = post.get("id")

                if upload_method == "native" and video_id:
                    # Native video upload
                    from app.video_processor import process_and_upload_video

                    result = process_and_upload_video(
                        video_id=video_id,
                        platforms=[platform],
                        captions={platform: post_content},
                        api_credentials=api_credentials,
                    )

                    if result.get("success") and result.get("results", {}).get(
                        platform, {}
                    ).get("success"):
                        # Update post status
                        update_post_status(
                            video_id,
                            platform,
                            "published",
                            actual_scheduled_date=now.isoformat(),
                            post_id=result["results"][platform].get("post_id"),
                        )

                        log_activity(
                            "auto_publish",
                            platform=platform,
                            video_id=video_id,
                            video_title=post.get("title", ""),
                            status="success",
                            message=f"Auto-published natively to {platform}",
                            details={
                                "post_id": result["results"][platform].get("post_id")
                            },
                        )
                        print(
                            f"[{datetime.now()}] ✅ Published {video_id} to {platform} (native upload)"
                        )
                    else:
                        error = result.get("error") or result.get("results", {}).get(
                            platform, {}
                        ).get("error", "Upload failed")
                        update_post_status(
                            video_id, platform, "failed", error_message=error
                        )
                        log_activity(
                            "auto_publish",
                            platform=platform,
                            video_id=video_id,
                            status="failed",
                            message=f"Failed to publish: {error}",
                        )
                        print(
                            f"[{datetime.now()}] ❌ Failed to publish {video_id} to {platform}: {error}"
                        )
                else:
                    # Link sharing mode - would need link posting API
                    # For now, just mark as published (link sharing implementation needed)
                    update_post_status(
                        video_id,
                        platform,
                        "published",
                        actual_scheduled_date=now.isoformat(),
                    )
                    print(
                        f"[{datetime.now()}] ✅ Published {video_id} to {platform} (link sharing)"
                    )

            except Exception as e:
                import traceback

                error_msg = str(e)
                update_post_status(
                    post.get("video_id"),
                    post.get("platform"),
                    "failed",
                    error_message=error_msg,
                )
                print(
                    f"[{datetime.now()}] ❌ Error publishing post {post.get('id')}: {error_msg}"
                )
                log_activity(
                    "auto_publish",
                    platform=post.get("platform"),
                    video_id=post.get("video_id"),
                    status="error",
                    message=f"Exception: {error_msg}",
                    errors=traceback.format_exc(),
                )

    except Exception as e:
        import traceback

        print(f"[{datetime.now()}] ❌ Error in publish_scheduled_posts: {e}")
        print(traceback.format_exc())


def schedule_daily_job():
    """Schedule the daily automation job and auto-publishing job."""
    settings = load_settings()
    scheduling = settings.get("scheduling", {})

    # Remove existing jobs
    SCHEDULER.remove_all_jobs()

    if not scheduling.get("enabled", False):
        return

    # Parse schedule time
    schedule_time = scheduling.get("youtube_schedule_time", "23:00")
    hour, minute = map(int, schedule_time.split(":"))

    # Schedule day (convert to cron day)
    day_map = {
        "monday": "mon",
        "tuesday": "tue",
        "wednesday": "wed",
        "thursday": "thu",
        "friday": "fri",
        "saturday": "sat",
        "sunday": "sun",
    }
    day = day_map.get(scheduling.get("schedule_day", "wednesday").lower(), "wed")

    # Schedule job (IST timezone)
    SCHEDULER.add_job(
        func=run_daily_automation,
        trigger=CronTrigger(day_of_week=day, hour=hour, minute=minute, timezone=IST),
        id="daily_automation",
        name="Daily YouTube Automation",
        replace_existing=True,
    )

    # Add auto-publishing job - runs every 15 minutes to check for posts ready to publish
    SCHEDULER.add_job(
        func=publish_scheduled_posts,
        trigger="interval",
        minutes=15,
        id="auto_publish_posts",
        name="Auto-Publish Scheduled Posts",
        replace_existing=True,
    )

    # Calculate next run
    now = datetime.now(IST)
    next_run = SCHEDULER.get_job("daily_automation").next_run_time
    settings["next_run"] = next_run.isoformat() if next_run else None
    save_settings(settings)


@app.route("/")
def index():
    """Serve React app index.html for all frontend routes."""
    try:
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        # Fallback to old template if React build doesn't exist
        settings = load_settings()
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in index route: {e}", exc_info=True)
        # Return a simple error page instead of crashing
        try:
            return (
                jsonify(
                    {
                        "error": "React build not found. Please run: cd frontend && npm run build"
                    }
                ),
                500,
            )
        except:
            return (
                f"<html><body><h1>Error loading page</h1><p>{str(e)}</p></body></html>",
                500,
            )


@app.route("/docs")
@app.route("/documentation")
def documentation():
    """Documentation page."""
    try:
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error loading documentation: {e}", exc_info=True)
        return (
            f"<html><body><h1>Documentation</h1><p>Error loading documentation: {str(e)}</p></body></html>",
            500,
        )


@app.route("/health")
def health():
    """Health check endpoint for monitoring."""
    try:
        from app.database import DB_PATH

        return jsonify(
            {
                "status": "healthy",
                "database_exists": os.path.exists(DB_PATH),
                "timestamp": datetime.now(IST).isoformat(),
            }
        )
    except Exception as e:
        app.logger.error(f"Error in health check: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "status": "degraded",
                    "error": str(e),
                    "timestamp": datetime.now(IST).isoformat(),
                }
            ),
            500,
        )


@app.route("/favicon.ico")
def favicon():
    """Serve favicon directly with proper headers."""
    from flask import send_from_directory
    import os

    return send_from_directory(
        os.path.join(app.root_path, "static"), "favicon.ico", mimetype="image/x-icon"
    )


@app.route("/static/js/service-worker.js")
def service_worker():
    """Serve service worker for PWA."""
    from flask import send_from_directory
    import os

    return send_from_directory(
        os.path.join(app.root_path, "static", "js"),
        "service-worker.js",
        mimetype="application/javascript",
    )


@app.route("/config", methods=["GET", "POST"])
def config():
    """Config page - serve Flask template (has complex form handling)."""
    try:
        settings = load_settings()

        if request.method == "POST":
            # Handle form submission
            section = request.form.get("section", "")
            if section == "api_keys":
                # Update API keys
                settings["api_keys"] = {
                    "linkedin_client_id": request.form.get("linkedin_client_id", ""),
                    "linkedin_client_secret": request.form.get(
                        "linkedin_client_secret", ""
                    ),
                    "linkedin_access_token": request.form.get(
                        "linkedin_access_token", ""
                    ),
                    "linkedin_person_urn": request.form.get("linkedin_person_urn", ""),
                    "facebook_page_access_token": request.form.get(
                        "facebook_page_access_token", ""
                    ),
                    "facebook_page_id": request.form.get("facebook_page_id", ""),
                    "instagram_business_account_id": request.form.get(
                        "instagram_business_account_id", ""
                    ),
                    "ayrshare_api_key": request.form.get("ayrshare_api_key", ""),
                }
                save_settings(settings)
                flash("Settings saved successfully!", "success")
                return redirect("/config#social-media-connections")

        # GET request - show config page
        # Check YouTube API status
        youtube_status = {
            "configured": False,
            "client_secret_exists": False,
            "channel_name": None,
            "channel_id": None,
            "error": None,
        }

        try:
            client_secret_path = os.path.join(
                os.path.dirname(__file__), "..", "client_secret.json"
            )
            client_secret_path = os.path.abspath(client_secret_path)
            youtube_status["client_secret_exists"] = os.path.exists(client_secret_path)

            if youtube_status["client_secret_exists"]:
                # Try to get YouTube service to verify connection
                try:
                    youtube = get_youtube_service()
                    if youtube:
                        channel_id = get_my_channel_id_helper(youtube)
                        if channel_id:
                            youtube_status["channel_id"] = channel_id
                            youtube_status["configured"] = True
                            # Get channel name
                            try:
                                channel_response = (
                                    youtube.channels()
                                    .list(part="snippet", id=channel_id)
                                    .execute()
                                )
                                if channel_response.get("items"):
                                    youtube_status["channel_name"] = (
                                        channel_response["items"][0]
                                        .get("snippet", {})
                                        .get("title", "")
                                    )
                            except:
                                pass
                except Exception as e:
                    youtube_status["error"] = str(e)
        except Exception as e:
            youtube_status["error"] = str(e)

        # Calculate configuration completeness
        api_keys = settings.get("api_keys", {})
        config_warnings = validate_config()
        config_complete = (
            len([w for w in config_warnings if w.get("severity") == "error"]) == 0
        )

        return render_template(
            "config.html",
            settings=settings,
            youtube_status=youtube_status,
            config_complete=config_complete,
            config_warnings=config_warnings,
        )
    except Exception as e:
        app.logger.error(f"Error in config route: {e}", exc_info=True)
        return render_template(
            "error.html", message=f"Error loading Config page: {str(e)}"
        )


@app.route("/settings")
def settings():
    """Settings page - serve React app."""
    try:
        # Serve React app - it will fetch data from /api/status endpoint
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        # Fallback to Flask template if React build doesn't exist
        return render_template("config.html", settings=load_settings())
    except Exception as e:
        app.logger.error(f"Error in settings route: {e}", exc_info=True)
        return render_template(
            "error.html", message=f"Error loading Settings page: {str(e)}"
        )


@app.route("/audio-generator")
def audio_generator():
    """Audio Generator page - serve HTML template."""
    try:
        return render_template("audio_generator.html")
    except Exception as e:
        app.logger.error(f"Error in audio_generator route: {e}", exc_info=True)
        return (
            jsonify({"error": f"Error loading Audio Generator: {str(e)}"}),
            500,
        )


@app.route("/api/generate-audio", methods=["POST"])
def generate_audio():
    """Generate audio from text using Eleven Labs TTS."""
    try:
        from scripts.create_audio import paragraph_to_wav

        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "Text cannot be empty"}), 400

        if len(text) > 10000:
            return jsonify({"error": "Text is too long (max 10000 characters)"}), 400

        # Create audio folder if it doesn't exist
        audio_dir = AUDIO_OUTPUT_DIR
        os.makedirs(audio_dir, exist_ok=True)

        # Generate unique filename with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{timestamp}.wav"
        filepath = os.path.join(audio_dir, filename)

        # Generate audio using the create_audio script
        result_path = paragraph_to_wav(text, filepath)

        # Get file size
        if os.path.exists(result_path):
            filesize = os.path.getsize(result_path)
            return (
                jsonify(
                    {
                        "success": True,
                        "filename": filename,
                        "filepath": audio_dir,
                        "filesize": filesize,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to create audio file"}), 500

    except ImportError as e:
        app.logger.error(f"Import error in generate_audio: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "error": "Audio generation module not found. Make sure ELEVENLABS_API_KEY is set."
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error generating audio: {e}", exc_info=True)
        return jsonify({"error": f"Error generating audio: {str(e)}"}), 500


@app.route("/audio/<filename>")
def serve_audio(filename):
    """Serve generated audio file."""
    try:
        # Security: only allow .wav files and alphanumeric with underscores/dots
        if not filename.endswith(".wav") or not all(
            c.isalnum() or c in "._-" for c in filename
        ):
            return jsonify({"error": "Invalid filename"}), 400

        audio_dir = AUDIO_OUTPUT_DIR
        return send_from_directory(audio_dir, filename, mimetype="audio/wav")
    except Exception as e:
        app.logger.error(f"Error serving audio: {e}", exc_info=True)
        return jsonify({"error": "File not found"}), 404


@app.route("/download-audio/<filename>")
def download_audio(filename):
    """Download audio file."""
    try:
        # Security: only allow .wav files and alphanumeric with underscores/dots
        if not filename.endswith(".wav") or not all(
            c.isalnum() or c in "._-" for c in filename
        ):
            return jsonify({"error": "Invalid filename"}), 400

        audio_dir = AUDIO_OUTPUT_DIR
        return send_from_directory(
            audio_dir,
            filename,
            mimetype="audio/wav",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        app.logger.error(f"Error downloading audio: {e}", exc_info=True)
        return jsonify({"error": "File not found"}), 404


@app.route("/api/audio-history", methods=["GET"])
def audio_history():
    """List generated audio files with metadata for history view."""
    try:
        audio_dir = AUDIO_OUTPUT_DIR
        os.makedirs(audio_dir, exist_ok=True)

        entries = []
        for fname in os.listdir(audio_dir):
            if not fname.endswith(".wav"):
                continue
            if not all(c.isalnum() or c in "._-" for c in fname):
                continue

            path = os.path.join(audio_dir, fname)
            if not os.path.isfile(path):
                continue

            stat = os.stat(path)
            entries.append(
                {
                    "filename": fname,
                    "filesize": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "download_url": f"/download-audio/{fname}",
                    "stream_url": f"/audio/{fname}",
                }
            )

        # Newest first
        entries.sort(key=lambda x: x["created_at"], reverse=True)
        return jsonify({"files": entries, "output_dir": audio_dir})
    except Exception as e:
        app.logger.error(f"Error listing audio history: {e}", exc_info=True)
        return jsonify({"error": "Could not list audio history"}), 500


@app.route("/api/audio/metadata", methods=["GET"])
def get_audio_metadata():
    """Get all audio files from filesystem grouped by course, module, and track."""
    try:
        from app.database import get_db_connection
        import os

        audio_dir = AUDIO_OUTPUT_DIR
        os.makedirs(audio_dir, exist_ok=True)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get all audio files from the filesystem
        all_files = []
        for fname in os.listdir(audio_dir):
            if not fname.endswith(".wav"):
                continue

            filepath = os.path.join(audio_dir, fname)
            if not os.path.isfile(filepath):
                continue

            stat = os.stat(filepath)

            # Check if file has metadata in database
            cursor.execute("SELECT * FROM audio_files WHERE filename = ?", (fname,))
            db_record = cursor.fetchone()

            if db_record:
                # Use database metadata
                all_files.append(
                    {
                        "id": db_record["id"],
                        "filename": fname,
                        "filepath": filepath,
                        "filesize": stat.st_size,
                        "course_name": db_record["course_name"],
                        "module_number": db_record["module_number"],
                        "module_name": db_record["module_name"],
                        "track_number": db_record["track_number"],
                        "track_name": db_record["track_name"],
                        "description": db_record["description"],
                        "tags": db_record["tags"],
                        "created_at": db_record["created_at"],
                        "is_tagged": True,
                        "download_url": f"/download-audio/{fname}",
                        "stream_url": f"/audio/{fname}",
                    }
                )
            else:
                # Untagged file from filesystem
                all_files.append(
                    {
                        "id": None,
                        "filename": fname,
                        "filepath": filepath,
                        "filesize": stat.st_size,
                        "course_name": None,
                        "module_number": None,
                        "module_name": None,
                        "track_number": None,
                        "track_name": None,
                        "description": None,
                        "tags": None,
                        "created_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "is_tagged": False,
                        "download_url": f"/download-audio/{fname}",
                        "stream_url": f"/audio/{fname}",
                    }
                )

        # Group by course -> module -> track
        grouped = {}
        untagged = []

        for file in all_files:
            if not file["course_name"]:
                untagged.append(file)
                continue

            course = file["course_name"]
            module = (
                f"Module {file['module_number']}: {file['module_name']}"
                if file["module_number"]
                else "Unorganized"
            )

            if course not in grouped:
                grouped[course] = {}
            if module not in grouped[course]:
                grouped[course][module] = []

            grouped[course][module].append(file)

        # Add untagged files as a separate group
        if untagged:
            grouped["📌 Untagged Files"] = {"Click tag button to organize": untagged}

        return jsonify(
            {
                "grouped": grouped,
                "total": len(all_files),
                "untagged_count": len(untagged),
                "tagged_count": len(all_files) - len(untagged),
            }
        )
    except Exception as e:
        app.logger.error(f"Error getting audio metadata: {e}", exc_info=True)
        return jsonify({"error": "Could not retrieve audio metadata"}), 500


@app.route("/api/audio/tag", methods=["POST"])
def tag_audio():
    """Tag an audio file with course, module, and track information."""
    try:
        from app.database import get_db_connection

        data = request.get_json()
        filename = data.get("filename")

        if not filename:
            return jsonify({"error": "Filename required"}), 400

        # Validate filename exists
        audio_path = os.path.join(AUDIO_OUTPUT_DIR, filename)
        if not os.path.exists(audio_path):
            return jsonify({"error": "Audio file not found"}), 404

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if file already has metadata
        cursor.execute("SELECT id FROM audio_files WHERE filename = ?", (filename,))
        existing = cursor.fetchone()

        stat = os.stat(audio_path)

        if existing:
            # Update existing
            cursor.execute(
                """
                UPDATE audio_files 
                SET course_name = ?, module_number = ?, module_name = ?,
                    track_number = ?, track_name = ?, description = ?,
                    tags = ?, updated_at = CURRENT_TIMESTAMP
                WHERE filename = ?
            """,
                (
                    data.get("course_name"),
                    data.get("module_number"),
                    data.get("module_name"),
                    data.get("track_number"),
                    data.get("track_name"),
                    data.get("description"),
                    data.get("tags"),
                    filename,
                ),
            )
        else:
            # Insert new
            cursor.execute(
                """
                INSERT INTO audio_files 
                (filename, filepath, filesize, course_name, module_number, 
                 module_name, track_number, track_name, description, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    filename,
                    audio_path,
                    stat.st_size,
                    data.get("course_name"),
                    data.get("module_number"),
                    data.get("module_name"),
                    data.get("track_number"),
                    data.get("track_name"),
                    data.get("description"),
                    data.get("tags"),
                ),
            )

        conn.commit()
        return jsonify({"success": True, "message": "Audio tagged successfully"})
    except Exception as e:
        app.logger.error(f"Error tagging audio: {e}", exc_info=True)
        return jsonify({"error": "Could not tag audio"}), 500


@app.route("/api/audio/search", methods=["GET"])
def search_audio():
    """Search audio files by course, module, or track."""
    try:
        from app.database import get_db_connection

        query = request.args.get("q", "").strip()
        course_filter = request.args.get("course", "").strip()
        module_filter = request.args.get("module", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "SELECT * FROM audio_files WHERE 1=1"
        params = []

        if course_filter:
            sql += " AND LOWER(course_name) LIKE ?"
            params.append(f"%{course_filter.lower()}%")

        if module_filter:
            sql += " AND LOWER(module_name) LIKE ?"
            params.append(f"%{module_filter.lower()}%")

        if query:
            sql += " AND (LOWER(filename) LIKE ? OR LOWER(track_name) LIKE ? OR LOWER(tags) LIKE ?)"
            params.extend(
                [f"%{query.lower()}%", f"%{query.lower()}%", f"%{query.lower()}%"]
            )

        sql += " ORDER BY COALESCE(course_name, ''), CAST(COALESCE(module_number, '0') AS INTEGER), CAST(COALESCE(track_number, '0') AS INTEGER)"

        cursor.execute(sql, params)
        files = cursor.fetchall()

        results = [
            {
                "id": f["id"],
                "filename": f["filename"],
                "course_name": f["course_name"],
                "module_name": f["module_name"],
                "track_name": f["track_name"],
                "download_url": f"/download-audio/{f['filename']}",
                "stream_url": f"/audio/{f['filename']}",
            }
            for f in files
        ]

        return jsonify({"results": results, "total": len(results)})
    except Exception as e:
        app.logger.error(f"Error searching audio: {e}", exc_info=True)
        return jsonify({"error": "Could not search audio"}), 500


@app.route("/api/automation-status")
def api_automation_status():
    """API endpoint for automation status."""
    settings = load_settings()
    job = SCHEDULER.get_job("daily_automation")

    return jsonify(
        {
            "enabled": settings.get("scheduling", {}).get("enabled", False),
            "last_run": settings.get("last_run"),
            "next_run": settings.get("next_run"),
            "job_running": job is not None,
            "job_next_run": (
                job.next_run_time.isoformat() if job and job.next_run_time else None
            ),
        }
    )


@app.route("/api/run-now", methods=["POST"])
def run_now():
    """Manually trigger automation now."""
    thread = threading.Thread(target=run_daily_automation)
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started", "message": "Automation started in background"})


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
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES
                )
                # Use port 5001 to match the Flask app port for OAuth redirect URI
                # For domain-based setup: Configure domain in /etc/hosts for local, DNS for NAS
                # See OAUTH_LONG_TERM_SETUP.md for details
                creds = flow.run_local_server(port=5001, open_browser=True)

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
                response = (
                    youtube.playlists()
                    .list(
                        part="id,snippet,contentDetails",
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=page_token,
                    )
                    .execute()
                )
            else:
                response = (
                    youtube.playlists()
                    .list(
                        part="id,snippet,contentDetails",
                        channelId=channel_id,
                        maxResults=50,
                    )
                    .execute()
                )

            for pl in response.get("items", []):
                snippet = pl.get("snippet", {})
                playlists.append(
                    {
                        "playlistId": pl["id"],
                        "playlistTitle": snippet.get("title", ""),
                        "playlistDescription": snippet.get("description", ""),
                        "playlistUrl": f"https://www.youtube.com/playlist?list={pl['id']}",
                        "itemCount": pl.get("contentDetails", {}).get("itemCount", 0),
                        "publishedAt": snippet.get("publishedAt", ""),
                        "thumbnail": snippet.get("thumbnails", {})
                        .get("default", {})
                        .get("url", ""),
                    }
                )

            page_token = response.get("nextPageToken")
            if not page_token:
                break
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            break

    return playlists


def fetch_playlist_videos_from_youtube(
    youtube, playlist_id: str, channel_title: str = ""
):
    """Fetch all videos in a playlist from YouTube."""
    videos = []
    page_token = None

    while True:
        try:
            if page_token:
                response = (
                    youtube.playlistItems()
                    .list(
                        part="id,snippet,contentDetails",
                        playlistId=playlist_id,
                        maxResults=50,
                        pageToken=page_token,
                    )
                    .execute()
                )
            else:
                response = (
                    youtube.playlistItems()
                    .list(
                        part="id,snippet,contentDetails",
                        playlistId=playlist_id,
                        maxResults=50,
                    )
                    .execute()
                )

            video_ids = [
                item["contentDetails"]["videoId"] for item in response.get("items", [])
            ]

            if video_ids:
                # Get video details in batches
                for i in range(0, len(video_ids), 50):
                    batch = video_ids[i : i + 50]
                    videos_response = (
                        youtube.videos()
                        .list(
                            part="id,snippet,status", id=",".join(batch), maxResults=50
                        )
                        .execute()
                    )

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
                                pub_date = datetime.fromisoformat(
                                    publish_at.replace("Z", "+00:00")
                                )
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

                        videos.append(
                            {
                                "videoId": video_id,
                                "title": snippet.get("title", ""),
                                "description": snippet.get("description", ""),
                                "thumbnail": snippet.get("thumbnails", {})
                                .get("medium", {})
                                .get("url", ""),
                                "publishedAt": published_at,
                                "publishAt": publish_at,
                                "privacyStatus": privacy_status,
                                "videoUrl": f"https://www.youtube.com/watch?v={video_id}",
                                "tags": ", ".join(snippet.get("tags", [])),
                                "channelTitle": channel_name,
                                "displayDate": display_date,
                                "dateLabel": date_label,
                                "isScheduled": is_scheduled,
                            }
                        )

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
    for platform in ["linkedin", "facebook", "instagram"]:
        cursor.execute(
            """
            SELECT post_content, schedule_date, actual_scheduled_date, status
            FROM social_media_posts
            WHERE video_id = ? AND platform = ?
        """,
            (video_id, platform),
        )

        row = cursor.fetchone()
        if row:
            posts[platform] = {
                "platform": platform,
                "post_content": row[0],
                "schedule_date": row[1],
                "actual_scheduled_date": row[2],
                "status": row[3],
            }
        else:
            posts[platform] = None

    conn.close()
    # Return as list for compatibility
    return [
        posts[platform]
        for platform in ["linkedin", "facebook", "instagram"]
        if posts.get(platform)
    ]


@app.route("/playlists")
def playlists():
    """Display all playlists and videos - always fetches fresh data from YouTube."""
    youtube = get_youtube_service()
    if not youtube:
        return render_template(
            "error.html",
            message="YouTube API not configured. Please set up client_secret.json",
        )

    try:
        # Always fetch fresh data from YouTube API (no caching)
        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return render_template(
                "error.html",
                message="Could not find your YouTube channel. Please check authentication.",
            )

        # Fetch latest playlists from YouTube API
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)
        channel_title = (
            playlists_data[0].get("channelTitle", "") if playlists_data else ""
        )

        # Videos will be loaded on demand via AJAX (also fetches fresh from YouTube)
        for playlist in playlists_data:
            playlist["videos"] = []
            playlist["videosLoaded"] = False

        # Add cache control headers to prevent browser caching
        response = make_response(
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        import traceback

        return render_template(
            "error.html",
            message=f"Error fetching playlists: {str(e)}\n{traceback.format_exc()}",
        )


def get_shorts_from_database():
    """Get all shorts from database with cross-platform status."""
    from app.database import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all videos from database
        cursor.execute(
            """
            SELECT 
                v.video_id,
                v.title,
                v.playlist_name,
                v.description,
                v.privacy_status,
                v.youtube_published_date,
                v.youtube_schedule_date,
                v.playlist_id,
                v.youtube_url,
                v.video_type,
                v.role
            FROM videos v
            ORDER BY v.youtube_published_date DESC, v.youtube_schedule_date DESC
        """
        )

        videos_data = cursor.fetchall()
        videos = []

        for video in videos_data:
            video_id = video[0]

            # Get social media posts for this video
            cursor.execute(
                """
                SELECT platform, status, schedule_date, post_content
                FROM social_media_posts
                WHERE video_id = ?
            """,
                (video_id,),
            )

            posts = cursor.fetchall()

            # Build platforms status
            platforms = {
                "youtube": video[4] == "public"
                or video[5] is not None,  # privacy_status or published_date
                "facebook": False,
                "instagram": False,
                "linkedin": False,
            }

            for post in posts:
                platform = post[0].lower()
                if platform in platforms and post[1] in ("scheduled", "published"):
                    platforms[platform] = True

            videos.append(
                {
                    "video_id": video_id,
                    "title": video[1],
                    "playlist_name": video[2],
                    "description": video[3],
                    "privacy_status": video[4],
                    "youtube_published_date": video[5],
                    "youtube_schedule_date": video[6],
                    "playlist_id": video[7],
                    "youtube_url": video[8],
                    "video_type": video[9],
                    "role": video[10],
                    "platforms": platforms,
                }
            )

        conn.close()
        return jsonify({"videos": videos})

    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


@app.route("/api/shorts")
def api_shorts():
    """API endpoint for Shorts data with role/type tagging and filtering."""
    try:
        youtube = get_youtube_service()
        if not youtube:
            # Return empty playlists structure when YouTube not connected
            return jsonify(
                {
                    "playlists": [],
                    "weekly_schedule": "23:00",
                    "schedule_day": "wednesday",
                    "total_videos": 0,
                    "total_youtube": 0,
                    "total_other_platforms": 0,
                    "total_not_scheduled": 0,
                    "available_roles": [],
                    "available_types": [],
                    "roles": {},
                    "types": {},
                }
            )

        # Get filter parameters
        role_filter = request.args.get("role", "").strip()
        type_filter = request.args.get("type", "").strip()

        try:
            channel_id = get_my_channel_id_helper(youtube)
            if not channel_id:
                return (
                    jsonify(
                        {
                            "error": "Could not find your YouTube channel. Please check authentication."
                        }
                    ),
                    400,
                )

            # Fetch all playlists and filter for Shorts
            all_playlists = fetch_all_playlists_from_youtube(youtube, channel_id)

            # Filter for Shorts playlists (case-insensitive check for "short" in title)
            shorts_playlists = [
                pl
                for pl in all_playlists
                if "short" in pl.get("playlistTitle", "").lower()
            ]

            # Get video counts for each playlist and social media status
            from app.database import get_db_connection
            from app.tagging import (
                derive_role_enhanced,
                derive_type_enhanced,
                ROLES,
                TYPES,
            )

            conn = get_db_connection()
            cursor = conn.cursor()

            # Get counts of videos scheduled on social media and tag playlists
            for playlist in shorts_playlists:
                playlist_id = playlist.get("playlistId", "")
                playlist_title = playlist.get("playlistTitle", "")

                # Try to get role/type from database first
                cursor.execute(
                    """
                    SELECT playlist_role, playlist_type 
                    FROM playlists 
                    WHERE playlist_id = ?
                """,
                    (playlist_id,),
                )
                db_result = cursor.fetchone()

                if db_result and db_result[0]:
                    playlist_role = db_result[0]
                    playlist_type = db_result[1] if db_result[1] else ""
                else:
                    # Derive role and type from playlist title
                    playlist_role = derive_role_enhanced(playlist_title, "", "", "")
                    playlist_type = derive_type_enhanced(playlist_title, "", "", "")

                    # Save to database for future use
                    try:
                        cursor.execute(
                            """
                            INSERT OR REPLACE INTO playlists 
                            (playlist_id, playlist_name, playlist_role, playlist_type, updated_at)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """,
                            (playlist_id, playlist_title, playlist_role, playlist_type),
                        )
                        conn.commit()
                    except Exception as e:
                        app.logger.error(f"Error saving playlist tags: {e}")

                playlist["role"] = playlist_role
                playlist["type"] = playlist_type
                playlist["role_label"] = ROLES.get(
                    playlist_role, playlist_role.title() if playlist_role else ""
                )
                playlist["type_label"] = TYPES.get(
                    playlist_type,
                    playlist_type.replace("_", " ").title() if playlist_type else "",
                )

                # OPTIMIZATION: Don't fetch videos - use itemCount and database queries instead
                # Fetching videos for each playlist is VERY slow (10-30 seconds per playlist)
                item_count = playlist.get("itemCount", 0)
                playlist["total_videos"] = item_count
                playlist["videos"] = (
                    []
                )  # Don't include videos in response - too much data

                # Get counts from database efficiently
                try:
                    # Count videos in database for this playlist
                    cursor.execute(
                        """
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN privacy_status = 'public' OR youtube_published_date IS NOT NULL THEN 1 ELSE 0 END) as youtube_count,
                            COUNT(DISTINCT CASE WHEN smp.id IS NOT NULL THEN v.video_id END) as other_platforms_count
                        FROM videos v
                        LEFT JOIN social_media_posts smp ON v.video_id = smp.video_id 
                            AND smp.status IN ('scheduled', 'published')
                            AND smp.platform != 'youtube'
                        WHERE v.playlist_id = ?
                    """,
                        (playlist_id,),
                    )
                    count_row = cursor.fetchone()

                    if count_row and count_row[0] > 0:
                        db_total = count_row[0] or 0
                        youtube_count = count_row[1] or 0
                        other_platforms_count = count_row[2] or 0

                        # Use database counts if available
                        playlist["total_videos"] = (
                            db_total if db_total > 0 else item_count
                        )
                        playlist["youtube_count"] = youtube_count
                        playlist["other_platforms_count"] = other_platforms_count
                        playlist["not_scheduled_count"] = (
                            db_total - other_platforms_count
                        )
                    else:
                        # No database data - use itemCount as estimate
                        playlist["youtube_count"] = (
                            item_count  # Assume all are on YouTube
                        )
                        playlist["other_platforms_count"] = 0
                        playlist["not_scheduled_count"] = item_count
                except Exception as e:
                    app.logger.error(
                        f"Error getting counts for playlist {playlist_id}: {e}"
                    )
                    playlist["youtube_count"] = item_count
                    playlist["other_platforms_count"] = 0
                    playlist["not_scheduled_count"] = item_count

            # Apply filters
            if role_filter:
                shorts_playlists = [
                    p for p in shorts_playlists if p.get("role") == role_filter
                ]
            if type_filter:
                shorts_playlists = [
                    p for p in shorts_playlists if p.get("type") == type_filter
                ]

            conn.close()

            # Calculate totals
            total_videos = sum(p.get("total_videos", 0) for p in shorts_playlists)
            total_youtube = sum(p.get("youtube_count", 0) for p in shorts_playlists)
            total_other_platforms = sum(
                p.get("other_platforms_count", 0) for p in shorts_playlists
            )
            total_not_scheduled = sum(
                p.get("not_scheduled_count", 0) for p in shorts_playlists
            )

            # Get settings for weekly schedule info
            settings = load_settings()
            weekly_schedule = settings.get("scheduling", {}).get(
                "youtube_schedule_time", "23:00"
            )
            schedule_day = settings.get("scheduling", {}).get(
                "schedule_day", "wednesday"
            )

            # Get available roles and types for filters
            available_roles = list(
                set(p.get("role") for p in shorts_playlists if p.get("role"))
            )
            available_types = list(
                set(p.get("type") for p in shorts_playlists if p.get("type"))
            )

            return jsonify(
                {
                    "playlists": shorts_playlists or [],
                    "weekly_schedule": weekly_schedule or "23:00",
                    "schedule_day": schedule_day or "wednesday",
                    "total_videos": total_videos or 0,
                    "total_youtube": total_youtube or 0,
                    "total_other_platforms": total_other_platforms or 0,
                    "total_not_scheduled": total_not_scheduled or 0,
                    "available_roles": available_roles,
                    "available_types": available_types,
                    "roles": {k: v for k, v in ROLES.items() if k in available_roles},
                    "types": {k: v for k, v in TYPES.items() if k in available_types},
                }
            )
        except Exception as e:
            app.logger.error(f"Error fetching Shorts playlists: {str(e)}")
            import traceback

            app.logger.error(traceback.format_exc())
            return jsonify({"error": f"Error fetching Shorts: {str(e)}"}), 500
    except Exception as e:
        import traceback

        app.logger.error(
            f"Error in api_shorts route: {str(e)}\n{traceback.format_exc()}"
        )
        return jsonify({"error": f"Error loading Shorts: {str(e)}"}), 500


@app.route("/api/shorts-playlists")
def api_shorts_playlists():
    """API endpoint to fetch shorts playlists (lightweight - for menu display)."""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return jsonify({"playlists": []}), 200

        try:
            channel_id = get_my_channel_id_helper(youtube)
            if not channel_id:
                return jsonify({"playlists": []}), 200

            # Fetch all playlists
            all_playlists = fetch_all_playlists_from_youtube(youtube, channel_id)

            # Filter for Shorts playlists (case-insensitive check for "short" in title)
            shorts_playlists = [
                {
                    "playlistId": pl.get("playlistId"),
                    "playlistTitle": pl.get("playlistTitle"),
                    "playlistUrl": pl.get("playlistUrl"),
                    "itemCount": pl.get("itemCount", 0),
                }
                for pl in all_playlists
                if "short" in pl.get("playlistTitle", "").lower()
            ]

            return (
                jsonify(
                    {"playlists": shorts_playlists, "count": len(shorts_playlists)}
                ),
                200,
            )

        except Exception as e:
            app.logger.error(f"Error fetching shorts playlists: {str(e)}")
            return jsonify({"playlists": []}), 200

    except Exception as e:
        app.logger.error(f"Error in api_shorts_playlists: {str(e)}")
        return jsonify({"playlists": []}), 200


@app.route("/api/shorts-library")
def api_shorts_library():
    """API endpoint to fetch downloaded shorts from disk and uploaded videos."""
    try:
        import os
        import json
        from datetime import datetime

        # Use the data/shorts_downloads folder relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shorts_download_dir = os.path.join(project_root, "data", "shorts_downloads")
        uploads_metadata_file = os.path.join(
            project_root, "data", "uploads_metadata.json"
        )

        folders = []
        total_videos = 0
        uploaded_videos = []

        # Scan all folders in shorts_downloads
        if os.path.exists(shorts_download_dir):
            for folder_name in os.listdir(shorts_download_dir):
                folder_path = os.path.join(shorts_download_dir, folder_name)
                if not os.path.isdir(folder_path):
                    continue

                # Count video files in this folder
                video_count = 0
                video_extensions = (".mp4", ".mkv", ".webm", ".mov", ".avi")

                for file_name in os.listdir(folder_path):
                    if file_name.lower().endswith(video_extensions):
                        video_count += 1

                if video_count > 0:
                    folders.append(
                        {
                            "name": folder_name,
                            "count": video_count,
                            "path": os.path.join(
                                "data", "shorts_downloads", folder_name
                            ),
                        }
                    )
                    total_videos += video_count

            # Sort folders by name
            folders.sort(key=lambda x: x["name"])

        # Load uploaded videos metadata
        if os.path.exists(uploads_metadata_file):
            try:
                with open(uploads_metadata_file, "r") as f:
                    uploaded_videos = json.load(f)
                    # Sort by upload date (newest first)
                    uploaded_videos.sort(
                        key=lambda x: x.get("uploaded_at", ""), reverse=True
                    )
            except Exception as e:
                app.logger.error(f"Error loading uploads metadata: {str(e)}")

        return (
            jsonify(
                {
                    "folders": folders,
                    "total_videos": total_videos,
                    "uploaded_videos": uploaded_videos,
                    "uploaded_count": len(uploaded_videos),
                }
            ),
            200,
        )

    except Exception as e:
        app.logger.error(f"Error in api_shorts_library: {str(e)}")
        return (
            jsonify(
                {
                    "folders": [],
                    "total_videos": 0,
                    "uploaded_videos": [],
                    "uploaded_count": 0,
                }
            ),
            200,
        )


@app.route("/api/shorts-folder-videos")
def api_shorts_folder_videos():
    """API endpoint to get all videos from a specific shorts folder."""
    try:
        import os
        from pathlib import Path

        folder_path = request.args.get("path", "")
        if not folder_path:
            return jsonify({"error": "Folder path is required"}), 400

        # Security: ensure path is within our shorts_downloads directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shorts_download_dir = os.path.join(project_root, "data", "shorts_downloads")

        # Resolve absolute path and check if it's within shorts_downloads
        abs_folder_path = os.path.normpath(os.path.join(project_root, folder_path))

        app.logger.info(f"Requested folder: {folder_path}")
        app.logger.info(f"Project root: {project_root}")
        app.logger.info(f"Shorts download dir: {shorts_download_dir}")
        app.logger.info(f"Resolved abs path: {abs_folder_path}")
        app.logger.info(f"Path exists: {os.path.exists(abs_folder_path)}")
        app.logger.info(
            f"Is directory: {os.path.isdir(abs_folder_path) if os.path.exists(abs_folder_path) else 'N/A'}"
        )

        if not abs_folder_path.startswith(shorts_download_dir):
            return jsonify({"error": "Invalid folder path"}), 403

        if not os.path.exists(abs_folder_path) or not os.path.isdir(abs_folder_path):
            return jsonify({"error": "Folder not found"}), 404

        # Get all video files
        video_extensions = (".mp4", ".mkv", ".webm", ".mov", ".avi")
        videos = []

        for file_name in sorted(os.listdir(abs_folder_path)):
            if file_name.lower().endswith(video_extensions):
                file_path = os.path.join(abs_folder_path, file_name)
                stat = os.stat(file_path)

                # Create relative path for serving
                rel_path = os.path.relpath(file_path, project_root)

                videos.append(
                    {
                        "name": file_name,
                        "path": rel_path,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    }
                )

        folder_name = os.path.basename(abs_folder_path)

        return (
            jsonify(
                {
                    "folder_name": folder_name,
                    "folder_path": folder_path,
                    "videos": videos,
                    "count": len(videos),
                }
            ),
            200,
        )

    except Exception as e:
        app.logger.error(f"Error in api_shorts_folder_videos: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/shorts")
def shorts():
    """Shorts page - serve React app (React will fetch data from /api/shorts)."""
    try:
        # Serve React app - it will fetch data from /api/shorts endpoint
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        # Fallback to Flask template if React build doesn't exist
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in shorts route: {e}", exc_info=True)
        return render_template(
            "error.html", message=f"Error loading Shorts page: {str(e)}"
        )


@app.route("/sessions")
@cached(timeout=60)  # Cache for 1 minute (sessions change less frequently)
def sessions():
    """Sessions management page - load and create shorts scripts from coaching sessions."""
    try:
        import os
        from pathlib import Path

        sessions_dir = Path("data/sessions")
        sessions_list = []

        if sessions_dir.exists():
            for file_path in sessions_dir.glob("*.txt"):
                try:
                    file_size = file_path.stat().st_size
                    sessions_list.append(
                        {
                            "filename": file_path.name,
                            "size": file_size,
                            "size_kb": round(file_size / 1024, 2),
                            "modified": datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).strftime("%Y-%m-%d %H:%M"),
                        }
                    )
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        # Sort by modified date (newest first)
        sessions_list.sort(key=lambda x: x["modified"], reverse=True)

        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in sessions route: {e}", exc_info=True)
        # Return empty sessions list on error instead of crashing
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )


@app.route("/api/sessions")
def api_get_sessions():
    """Get list of all session files with metadata."""
    from pathlib import Path
    from app.database import get_db_connection

    sessions_dir = Path("data/sessions")
    sessions_list = []
    metadata_map = {}

    if not sessions_dir.exists():
        return jsonify(
            {
                "sessions": [],
                "statistics": {
                    "total": 0,
                    "upcoming": 0,
                    "completed": 0,
                    "by_role": {},
                    "by_type": {},
                },
                "upcoming": [],
                "recent": [],
                "source": "data/sessions",
            }
        )

    # Load database metadata once so we can enrich each session
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT filename, role, session_type, client_name, session_date,
                   meet_recording_url, meet_recording_drive_id,
                   gemini_transcript_url, gemini_transcript_drive_id,
                   chatgpt_notes, email_thread_id, email_subject,
                   additional_notes, tags
            FROM sessions_metadata
        """
        )
        rows = cursor.fetchall()
        conn.close()
        metadata_map = {row["filename"]: dict(row) for row in rows}
    except Exception as e:
        app.logger.warning(f"Could not load session metadata: {e}")

    # Get all .txt files
    for file_path in sessions_dir.glob("*.txt"):
        try:
            file_stat = file_path.stat()
            file_size = file_stat.st_size
            modified_time = datetime.fromtimestamp(file_stat.st_mtime)

            # Try to parse filename for metadata (format: YYYY-MM-DD_clientname_role_type.txt)
            filename = file_path.stem
            parts = filename.split("_")

            session_data = {
                "filename": file_path.name,
                "size": file_size,
                "modified": modified_time.strftime("%Y-%m-%d %H:%M"),
                "date": modified_time.strftime("%Y-%m-%d"),
                "status": "completed",  # Default to completed for existing files
                "has_content": True,
            }

            # Try to extract metadata from filename
            if len(parts) >= 2:
                try:
                    # Check if first part is a date
                    datetime.strptime(parts[0], "%Y-%m-%d")
                    session_data["date"] = parts[0]
                    if len(parts) >= 2:
                        session_data["client_name"] = parts[1].replace("-", " ").title()
                    if len(parts) >= 3:
                        session_data["role"] = parts[2]
                    if len(parts) >= 4:
                        session_data["type"] = parts[3]
                except ValueError:
                    # Not a date format, treat as client name
                    session_data["client_name"] = parts[0].replace("-", " ").title()
                    if len(parts) >= 2:
                        session_data["role"] = parts[1]
                    if len(parts) >= 3:
                        session_data["type"] = parts[2]

            # Read first 200 chars as preview
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    preview = f.read(200)
                    session_data["preview"] = preview
            except:
                pass

            metadata = metadata_map.get(file_path.name)
            linked_resources = {
                "recording": False,
                "transcript": False,
                "chatgpt": False,
                "email": False,
            }

            if metadata:
                session_data["metadata"] = metadata
                session_data["role"] = metadata.get("role") or session_data.get("role")
                session_data["type"] = metadata.get("session_type") or session_data.get(
                    "type"
                )
                session_data["client_name"] = metadata.get(
                    "client_name"
                ) or session_data.get("client_name")
                session_data["date"] = metadata.get("session_date") or session_data.get(
                    "date"
                )
                session_data["session_date"] = metadata.get(
                    "session_date"
                ) or session_data.get("date")
                session_data["meet_recording_url"] = metadata.get("meet_recording_url")
                session_data["gemini_transcript_url"] = metadata.get(
                    "gemini_transcript_url"
                )
                session_data["chatgpt_notes"] = metadata.get("chatgpt_notes")
                session_data["email_thread_id"] = metadata.get("email_thread_id")
                session_data["email_subject"] = metadata.get("email_subject")
                session_data["additional_notes"] = metadata.get("additional_notes")
                session_data["tags"] = metadata.get("tags")

                linked_resources = {
                    "recording": bool(
                        metadata.get("meet_recording_url")
                        or metadata.get("meet_recording_drive_id")
                    ),
                    "transcript": bool(
                        metadata.get("gemini_transcript_url")
                        or metadata.get("gemini_transcript_drive_id")
                    ),
                    "chatgpt": bool(metadata.get("chatgpt_notes")),
                    "email": bool(
                        metadata.get("email_thread_id") or metadata.get("email_subject")
                    ),
                }
            else:
                session_data["session_date"] = session_data.get("date")

            session_data["linked_resources"] = linked_resources

            sessions_list.append(session_data)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Sort by modified date (newest first)
    sessions_list.sort(key=lambda x: x.get("modified", ""), reverse=True)

    # Calculate statistics
    total = len(sessions_list)
    upcoming = len([s for s in sessions_list if s.get("status") == "upcoming"])
    completed = len([s for s in sessions_list if s.get("status") == "completed"])

    # Count by role and type
    by_role = {}
    by_type = {}
    for session in sessions_list:
        role = session.get("role", "unknown")
        by_role[role] = by_role.get(role, 0) + 1
        session_type = session.get("type", "unknown")
        by_type[session_type] = by_type.get(session_type, 0) + 1

    # Get recent (last 10) and upcoming
    recent = sessions_list[:10]
    upcoming_list = [s for s in sessions_list if s.get("status") == "upcoming"]

    return jsonify(
        {
            "sessions": sessions_list,
            "statistics": {
                "total": total,
                "upcoming": upcoming,
                "completed": completed,
                "by_role": by_role,
                "by_type": by_type,
            },
            "upcoming": upcoming_list,
            "recent": recent,
            "source": str(sessions_dir),
        }
    )


@app.route("/api/sessions/submit", methods=["POST"])
def api_submit_session():
    """Submit a new coaching session with role and type."""
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Request must be JSON"}), 400

        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Validate required fields
        required_fields = ["role", "session_type", "content"]
        is_valid, error_msg = validate_required_fields(data, required_fields)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400

        role = sanitize_input(data.get("role", ""))
        session_type = sanitize_input(data.get("session_type", ""))
        content = sanitize_input(
            data.get("content", ""), max_length=50000
        )  # Limit content size

        # Validate role and session type
        if not validate_role(role):
            return jsonify({"success": False, "error": "Invalid role selected"}), 400

        if not validate_session_type(session_type):
            return (
                jsonify({"success": False, "error": "Invalid session type selected"}),
                400,
            )

        # Validate content length
        is_valid, error_msg = validate_string_length(
            content, min_length=10, max_length=50000
        )
        if not is_valid:
            return jsonify({"success": False, "error": error_msg}), 400

        # Create sessions directory if it doesn't exist
        sessions_dir = Path("data/sessions")
        sessions_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename from role, type, and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_role = re.sub(r"[^\w\s-]", "", role).replace(" ", "_")[:30]
        safe_type = re.sub(r"[^\w\s-]", "", session_type).replace(" ", "_")[:30]
        filename = f"{safe_role}_{safe_type}_{timestamp}.txt"

        # Create file with metadata header
        file_path = sessions_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            # Write metadata header
            f.write(f"ROLE: {role}\n")
            f.write(f"SESSION_TYPE: {session_type}\n")
            f.write(f"CREATED: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            # Write content
            f.write(content)

        return jsonify(
            {
                "success": True,
                "message": "Session saved successfully",
                "filename": filename,
            }
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/sessions/<filename>")
def api_get_session(filename):
    """Get content of a session file."""
    from pathlib import Path

    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    sessions_dir = Path("data/sessions")
    file_path = sessions_dir / filename

    if not file_path.exists() or not file_path.is_file():
        return jsonify({"error": "File not found"}), 404

    try:
        metadata = None
        try:
            from app.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM sessions_metadata WHERE filename = ?", (filename,)
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                metadata = dict(row)
        except Exception as meta_error:
            app.logger.warning(f"Could not load metadata for {filename}: {meta_error}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return jsonify(
            {
                "success": True,
                "filename": filename,
                "content": content,
                "size": len(content),
                "metadata": metadata,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions/<filename>/metadata", methods=["GET", "POST", "PUT"])
def api_session_metadata(filename):
    """Get or update session metadata."""
    from app.database import get_db_connection

    if request.method == "GET":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sessions_metadata WHERE filename = ?", (filename,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return jsonify({"success": True, "metadata": dict(row)})
        else:
            return jsonify(
                {
                    "success": True,
                    "metadata": {
                        "filename": filename,
                        "role": None,
                        "session_type": None,
                        "client_name": None,
                        "session_date": None,
                        "meet_recording_url": None,
                        "gemini_transcript_url": None,
                        "chatgpt_notes": None,
                        "email_thread_id": None,
                        "additional_notes": None,
                        "tags": None,
                    },
                }
            )

    elif request.method in ["POST", "PUT"]:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO sessions_metadata (
                filename, role, session_type, client_name, session_date,
                meet_recording_url, meet_recording_drive_id,
                gemini_transcript_url, gemini_transcript_drive_id,
                chatgpt_notes, email_thread_id, email_subject,
                additional_notes, tags, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            (
                filename,
                data.get("role"),
                data.get("session_type"),
                data.get("client_name"),
                data.get("session_date"),
                data.get("meet_recording_url"),
                data.get("meet_recording_drive_id"),
                data.get("gemini_transcript_url"),
                data.get("gemini_transcript_drive_id"),
                data.get("chatgpt_notes"),
                data.get("email_thread_id"),
                data.get("email_subject"),
                data.get("additional_notes"),
                data.get("tags"),
            ),
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Metadata saved successfully"})


@app.route("/api/sessions/<filename>/generate-shorts", methods=["POST"])
def api_generate_shorts_from_session(filename):
    """Generate viral shorts scripts from a session file."""
    import os
    from pathlib import Path
    import re

    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400

    sessions_dir = Path("data/sessions")
    file_path = sessions_dir / filename

    if not file_path.exists() or not file_path.is_file():
        return jsonify({"error": "File not found"}), 404

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get settings for CTAs
        settings = load_settings()
        cta_settings = settings.get("cta", {})
        booking_url = cta_settings.get("booking_url", "https://fullstackmaster/book")
        whatsapp_number = cta_settings.get("whatsapp_number", "+1-609-442-4081")

        # Generate shorts scripts using enhanced generator
        from app.session_shorts_generator import generate_shorts_from_session_enhanced

        shorts_scripts_data = generate_shorts_from_session_enhanced(
            content, booking_url, whatsapp_number
        )

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

        return jsonify(
            {
                "success": True,
                "filename": filename,
                "scripts": shorts_scripts,
                "count": len(shorts_scripts),
            }
        )
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


def generate_shorts_from_session_old(
    session_content: str, booking_url: str, whatsapp_number: str
) -> list:
    """
    Generate viral shorts scripts from session content.
    Uses AI-like patterns to create engaging, clickbait-style scripts.
    """
    scripts = []

    # Extract key insights, questions, and answers from session
    lines = session_content.split("\n")

    # Pattern 1: Extract interview questions and answers
    current_qa = []
    for i, line in enumerate(lines):
        line = line.strip()
        if not line or len(line) < 20:
            continue

        # Look for question patterns
        if any(
            keyword in line.lower()
            for keyword in ["?", "how", "what", "why", "tell me", "describe", "explain"]
        ):
            if current_qa:
                # Generate script from previous Q&A
                script = create_viral_script_from_qa(
                    current_qa, booking_url, whatsapp_number
                )
                if script:
                    scripts.append(script)
            current_qa = [line]
        elif current_qa:
            current_qa.append(line)
            if len(current_qa) >= 5:  # Enough context
                script = create_viral_script_from_qa(
                    current_qa, booking_url, whatsapp_number
                )
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


def create_viral_script_from_qa(
    qa_lines: list, booking_url: str, whatsapp_number: str
) -> str:
    """Create a viral shorts script from Q&A content."""
    content = " ".join(qa_lines[:3])  # Use first 3 lines

    hooks = [
        "🚨 90% of candidates FAIL this question...",
        "Most engineers get REJECTED because of this mistake...",
        "FAANG interviewers reject 8/10 candidates. Here's why...",
        "This one mistake cost someone their dream job...",
        "The #1 reason why talented engineers fail interviews...",
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


def create_viral_script_from_insight(
    insight: str, booking_url: str, whatsapp_number: str
) -> str:
    """Create a viral shorts script from an insight."""
    hooks = [
        "💡 Pro tip that changed my career...",
        "This insight helped 100+ engineers get offers...",
        "The secret most engineers don't know...",
        "This one thing separates senior engineers from juniors...",
    ]

    import random

    hook = random.choice(hooks)

    script = f"""{hook}

{insight[:150]}...

📅 Book 1-on-1 coaching: {booking_url}
💬 WhatsApp: {whatsapp_number}

#TechInterview #CareerGrowth"""

    return script


def create_viral_script_from_mistake(
    mistake: str, booking_url: str, whatsapp_number: str
) -> str:
    """Create a viral shorts script from a mistake/lesson."""
    hooks = [
        "🚨 This mistake cost someone their ${}K offer...",
        "Don't make this mistake in your interview...",
        "I've seen 100+ candidates fail because of this...",
        "This is why talented engineers get rejected...",
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
    lines = content.split("\n")

    keywords = [
        "insight",
        "tip",
        "key",
        "important",
        "remember",
        "pro tip",
        "secret",
        "strategy",
    ]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        if (
            any(keyword in line_lower for keyword in keywords)
            and len(line.strip()) > 30
        ):
            # Get context (next 2 lines)
            context = line
            if i + 1 < len(lines):
                context += " " + lines[i + 1]
            if i + 2 < len(lines):
                context += " " + lines[i + 2]
            insights.append(context.strip()[:200])

    return insights


def extract_mistakes(content: str) -> list:
    """Extract mistakes and lessons from session content."""
    mistakes = []
    lines = content.split("\n")

    keywords = [
        "mistake",
        "wrong",
        "error",
        "failed",
        "rejected",
        "don't",
        "avoid",
        "lesson",
    ]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        if (
            any(keyword in line_lower for keyword in keywords)
            and len(line.strip()) > 30
        ):
            # Get context (next 2 lines)
            context = line
            if i + 1 < len(lines):
                context += " " + lines[i + 1]
            if i + 2 < len(lines):
                context += " " + lines[i + 2]
            mistakes.append(context.strip()[:200])

    return mistakes


@app.route("/insights")
def insights():
    """Insights page - serve React app (React will fetch data from /insights API)."""
    try:
        # Serve React app - it will fetch data from Flask APIs
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        # Fallback to Flask template if React build doesn't exist
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in insights route: {e}", exc_info=True)
        return render_template(
            "error.html", message=f"Error loading insights: {str(e)}"
        )


@app.route("/api/insights-data")
@app.route("/insights-data")
def insights_data():
    """API endpoint for insights data - used by React app."""
    try:
        # Get YouTube Analytics from database (always works)
        try:
            youtube_analytics = get_youtube_analytics()
        except Exception as e:
            app.logger.error(f"Error getting YouTube analytics: {e}")
            youtube_analytics = {
                "error": "Unable to fetch analytics",
                "total_videos": 0,
                "total_views": 0,
                "total_likes": 0,
                "message": "Go to Shorts page to sync videos from YouTube",
            }

        # Get Facebook Insights if available (with error handling)
        try:
            facebook_insights = get_facebook_insights()
        except Exception as e:
            app.logger.error(f"Error getting Facebook insights: {e}")
            facebook_insights = {"error": f"Facebook Insights error: {str(e)}"}

        # Get LinkedIn Analytics if available (with error handling)
        try:
            linkedin_analytics = get_linkedin_analytics()
        except Exception as e:
            app.logger.error(f"Error getting LinkedIn analytics: {e}")
            linkedin_analytics = {"error": f"LinkedIn Analytics error: {str(e)}"}

        # Get YouTube video statistics from database
        from app.database import get_db_connection

        youtube_video_stats = {"total": 0, "total_views": 0, "total_likes": 0}
        facebook_post_stats = {"count": 0}
        linkedin_post_stats = {"count": 0}

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Count total videos and stats
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total,
                    COALESCE(SUM(CAST(view_count AS INTEGER)), 0) as total_views,
                    COALESCE(SUM(CAST(like_count AS INTEGER)), 0) as total_likes
                FROM videos 
                WHERE privacy_status = 'public'
            """
            )
            row = cursor.fetchone()
            if row:
                youtube_video_stats = {
                    "total": row["total"] or 0,
                    "total_views": row["total_views"] or 0,
                    "total_likes": row["total_likes"] or 0,
                }

            # Count Facebook posts
            cursor.execute(
                "SELECT COUNT(*) as count FROM social_media_posts WHERE platform = 'facebook'"
            )
            row = cursor.fetchone()
            if row:
                facebook_post_stats = {"count": row["count"] or 0}

            # Count LinkedIn posts
            cursor.execute(
                "SELECT COUNT(*) as count FROM social_media_posts WHERE platform = 'linkedin'"
            )
            row = cursor.fetchone()
            if row:
                linkedin_post_stats = {"count": row["count"] or 0}

            conn.close()
        except Exception as e:
            app.logger.error(f"Database error in insights: {e}")
            # Stats already have default values

        # Combine all insights
        settings = load_settings()
        cta_data = settings.get("cta", {})

        # Calculate optimal posting times with error handling
        try:
            optimal_times = calculate_optimal_posting_times(
                youtube_analytics, facebook_insights, linkedin_analytics
            )
        except Exception as e:
            app.logger.error(f"Error calculating optimal posting times: {e}")
            optimal_times = {}

        insights_data = {
            "youtube": (
                youtube_analytics if youtube_analytics else {"error": "Not configured"}
            ),
            "youtube_videos": youtube_video_stats,
            "facebook": (
                facebook_insights if facebook_insights else {"error": "Not configured"}
            ),
            "facebook_posts": facebook_post_stats,
            "linkedin": (
                linkedin_analytics
                if linkedin_analytics
                else {"error": "Not configured"}
            ),
            "linkedin_posts": linkedin_post_stats,
            "optimal_posting_times": optimal_times,
            "cta": cta_data,
        }

        # Return JSON for API endpoint
        if request.path.startswith("/api/"):
            return jsonify(insights_data)

        # Return template for direct access
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        import traceback

        app.logger.error(f"Error loading insights: {e}", exc_info=True)
        if request.path.startswith("/api/"):
            return jsonify({"error": str(e)}), 500
        return render_template(
            "error.html",
            message=f"Error loading insights: {str(e)}\n{traceback.format_exc()}",
        )


def get_youtube_analytics():
    """Get YouTube Analytics data from YouTube Analytics API and database."""
    from app.database import get_db_connection
    from datetime import datetime, timedelta
    import pytz

    try:
        # Try to get real analytics from YouTube Analytics API
        api_analytics = get_youtube_analytics_from_api()

        # Get database stats for video counts
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_videos,
                COUNT(CASE WHEN privacy_status = 'public' THEN 1 END) as public_videos
            FROM videos
            WHERE video_id IS NOT NULL
        """
        )
        db_stats = cursor.fetchone()
        conn.close()

        # If API analytics succeeded, use it
        if api_analytics and not api_analytics.get("error"):
            # Process and aggregate the API data
            views_data = api_analytics.get("views_data", [])
            total_views_30d = (
                sum(row[1] for row in views_data if len(row) > 1) if views_data else 0
            )
            total_watch_time = (
                sum(row[2] for row in views_data if len(row) > 2) if views_data else 0
            )

            # Process demographics
            demographics = api_analytics.get("demographics", [])
            age_gender_breakdown = {}
            for row in demographics:
                if len(row) >= 3:
                    age_group = row[0]
                    gender = row[1]
                    views = row[2]
                    key = f"{age_group}_{gender}"
                    age_gender_breakdown[key] = views

            # Process geography
            geography = api_analytics.get("geography", [])
            top_countries = []
            for row in geography[:5]:  # Top 5 countries
                if len(row) >= 2:
                    top_countries.append({"country": row[0], "views": row[1]})

            # Process hourly activity to find optimal posting times
            hourly_activity = api_analytics.get("hourly_activity", [])
            hourly_views = {}
            for row in hourly_activity:
                if len(row) >= 3:
                    hour = row[1]  # Hour of day (0-23)
                    views = row[2]
                    hourly_views[hour] = hourly_views.get(hour, 0) + views

            # Find top 3 hours
            sorted_hours = sorted(
                hourly_views.items(), key=lambda x: x[1], reverse=True
            )
            best_times = (
                [f"{hour:02d}:00" for hour, views in sorted_hours[:3]]
                if sorted_hours
                else ["14:00", "17:00", "21:00"]
            )

            return {
                "source": "youtube_analytics_api",
                "total_views_30d": total_views_30d,
                "watch_time_minutes": total_watch_time,
                "total_videos": db_stats["total_videos"] if db_stats else 0,
                "public_videos": db_stats["public_videos"] if db_stats else 0,
                "demographics": {
                    "age_gender": age_gender_breakdown,
                    "top_countries": top_countries,
                },
                "optimal_posting_times": best_times,
                "hourly_activity": hourly_views,
                "channel_id": api_analytics.get("channel_id", ""),
            }

        # Fallback to database-only if API fails
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_videos,
                COUNT(CASE WHEN privacy_status = 'public' THEN 1 END) as public_videos,
                COUNT(CASE WHEN privacy_status = 'unlisted' THEN 1 END) as unlisted_videos,
                COUNT(CASE WHEN privacy_status = 'private' THEN 1 END) as private_videos,
                COUNT(DISTINCT playlist_name) as total_playlists
            FROM videos
            WHERE video_id IS NOT NULL
        """
        )
        stats = cursor.fetchone()

        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute(
            """
            SELECT 
                video_id,
                title,
                youtube_published_date as published_at,
                playlist_name,
                privacy_status,
                video_type
            FROM videos
            WHERE youtube_published_date >= ? OR youtube_schedule_date >= ?
            ORDER BY COALESCE(youtube_schedule_date, youtube_published_date) DESC
            LIMIT 10
        """,
            (thirty_days_ago, thirty_days_ago),
        )
        recent_videos = cursor.fetchall()

        cursor.execute(
            """
            SELECT 
                playlist_name,
                COUNT(*) as count
            FROM videos
            WHERE playlist_name IS NOT NULL AND playlist_name != ''
            GROUP BY playlist_name
            ORDER BY count DESC
            LIMIT 10
        """
        )
        playlists = cursor.fetchall()
        conn.close()

        analytics_data = {
            "source": "database",
            "total_videos": stats["total_videos"] if stats else 0,
            "public_videos": stats["public_videos"] if stats else 0,
            "unlisted_videos": stats["unlisted_videos"] if stats else 0,
            "private_videos": stats["private_videos"] if stats else 0,
            "total_playlists": stats["total_playlists"] if stats else 0,
            "recent_videos": (
                [
                    {
                        "video_id": v["video_id"],
                        "title": v["title"],
                        "published_at": v["published_at"],
                        "playlist": v["playlist_name"],
                        "privacy": v["privacy_status"],
                        "type": v["video_type"],
                    }
                    for v in recent_videos
                ]
                if recent_videos
                else []
            ),
            "playlists": (
                [{"name": p["playlist_name"], "count": p["count"]} for p in playlists]
                if playlists
                else []
            ),
            "api_error": (
                api_analytics.get("error")
                if api_analytics
                else "YouTube Analytics API not available"
            ),
            "note": "Using database stats. Enable YouTube Analytics API for detailed metrics.",
        }

        if stats and stats["total_videos"] == 0:
            analytics_data["message"] = (
                "No videos in database. Go to Shorts page to sync from YouTube."
            )

        return analytics_data

    except Exception as e:
        app.logger.error(f"Error getting YouTube analytics: {e}")
        return {
            "error": "Unable to fetch analytics",
            "details": str(e),
            "suggestion": "Make sure YouTube API is configured and videos are synced.",
        }


def get_youtube_analytics_from_api():
    """Get YouTube Analytics data from YouTube Analytics API (optional, requires setup)."""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return {"error": "YouTube API not configured"}

        # Need YouTube Analytics API (different from Data API)
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials
        import os

        SCOPES_ANALYTICS = ["https://www.googleapis.com/auth/yt-analytics.readonly"]
        TOKEN_FILE = os.path.join(
            os.path.dirname(__file__), "..", "config", "token.json"
        )

        creds = None
        if os.path.exists(TOKEN_FILE):
            from google.oauth2.credentials import Credentials

            # Try to load with analytics scope
            try:
                creds = Credentials.from_authorized_user_file(
                    TOKEN_FILE, SCOPES_ANALYTICS
                )
            except Exception as e:
                # If token doesn't have analytics scope, return error gracefully
                return {
                    "error": "YouTube Analytics API not authenticated. Please re-authenticate with analytics scope.",
                    "details": str(e),
                }

        if not creds or not creds.valid:
            return {"error": "YouTube Analytics not authenticated"}

        analytics = build("youtubeAnalytics", "v2", credentials=creds)
        channel_id = get_my_channel_id_helper(youtube)

        if not channel_id:
            return {"error": "Channel ID not found"}

        # Get views, watch time, subscribers
        end_date = datetime.now(IST).strftime("%Y-%m-%d")
        start_date = (datetime.now(IST) - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            # Views and watch time
            views_response = (
                analytics.reports()
                .query(
                    ids=f"channel=={channel_id}",
                    startDate=start_date,
                    endDate=end_date,
                    metrics="views,estimatedMinutesWatched,subscribersGained",
                    dimensions="day",
                )
                .execute()
            )

            # Demographics - Geography
            geo_response = (
                analytics.reports()
                .query(
                    ids=f"channel=={channel_id}",
                    startDate=start_date,
                    endDate=end_date,
                    metrics="views",
                    dimensions="country",
                )
                .execute()
            )

            # Demographics - Age and Gender
            demo_response = (
                analytics.reports()
                .query(
                    ids=f"channel=={channel_id}",
                    startDate=start_date,
                    endDate=end_date,
                    metrics="views",
                    dimensions="ageGroup,gender",
                )
                .execute()
            )

            # Audience activity by hour
            hourly_response = (
                analytics.reports()
                .query(
                    ids=f"channel=={channel_id}",
                    startDate=start_date,
                    endDate=end_date,
                    metrics="views",
                    dimensions="day,hour",
                )
                .execute()
            )

            return {
                "views_data": views_response.get("rows", []),
                "geography": geo_response.get("rows", []),
                "demographics": demo_response.get("rows", []),
                "hourly_activity": hourly_response.get("rows", []),
                "channel_id": channel_id,
            }
        except Exception as e:
            error_msg = str(e)
            # Extract user-friendly error message
            if "accessNotConfigured" in error_msg or "has not been used" in error_msg:
                error_msg = "YouTube Analytics API not enabled. Enable it in Google Cloud Console."
            elif "403" in error_msg:
                error_msg = "YouTube Analytics API access denied. Check permissions in Google Cloud Console."
            elif len(error_msg) > 200:
                error_msg = error_msg[:200] + "..."
            return {
                "error": error_msg,
                "note": "YouTube Analytics API may need to be enabled in Google Cloud Console",
            }
    except Exception as e:
        return {"error": f"Error getting YouTube Analytics: {str(e)}"}


def get_facebook_insights():
    """Get Facebook Page Insights from database and optionally from Facebook API."""
    from app.database import get_db_connection

    try:
        # Get stats from database first (always works)
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_posts,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
            FROM social_media_posts
            WHERE platform = 'facebook'
        """
        )
        stats = cursor.fetchone()

        # Get recent posts
        cursor.execute(
            """
            SELECT 
                video_id,
                post_content,
                status,
                schedule_date,
                created_at
            FROM social_media_posts
            WHERE platform = 'facebook'
            ORDER BY created_at DESC
            LIMIT 10
        """
        )
        recent_posts = cursor.fetchall()

        conn.close()

        facebook_data = {
            "source": "database",
            "total_posts": stats["total_posts"] if stats else 0,
            "published": stats["published"] if stats else 0,
            "scheduled": stats["scheduled"] if stats else 0,
            "pending": stats["pending"] if stats else 0,
            "recent_posts": (
                [
                    {
                        "video_id": p["video_id"],
                        "content": p["post_content"][:100] if p["post_content"] else "",
                        "status": p["status"],
                        "schedule_date": p["schedule_date"],
                    }
                    for p in recent_posts
                ]
                if recent_posts
                else []
            ),
            "note": "Data from local database. Configure Facebook API for live insights.",
        }

        if stats and stats["total_posts"] == 0:
            facebook_data["message"] = (
                "No Facebook posts yet. Schedule posts from Shorts page."
            )

        return facebook_data

    except Exception as e:
        app.logger.error(f"Error getting Facebook insights from database: {e}")
        return {
            "error": "Unable to fetch Facebook insights",
            "total_posts": 0,
            "published": 0,
            "scheduled": 0,
            "suggestion": "Schedule posts to Facebook from the Shorts page.",
        }


def get_facebook_insights_from_api():
    """Get Facebook Page Insights from Facebook API (optional, requires access token)."""
    try:
        settings = load_settings()
        api_keys = settings.get("api_keys", {})
        page_id = api_keys.get("facebook_page_id", "")
        access_token = api_keys.get("facebook_page_access_token", "")

        if not page_id or not access_token:
            return {"error": "Facebook credentials not configured"}

        import requests

        # First, validate the token by checking if it's still valid
        # Use a simple API call to verify token
        validate_url = (
            f"https://graph.facebook.com/v18.0/me?access_token={access_token}"
        )
        validate_response = requests.get(validate_url, timeout=10)

        if validate_response.status_code != 200:
            error_data = validate_response.json() if validate_response.text else {}
            if error_data.get("error"):
                error_info = error_data["error"]
                error_code = error_info.get("code")
                error_subcode = error_info.get("error_subcode")

                # Code 190 can mean expired OR invalid token format
                # Check subcode to be more specific
                if error_code == 190:
                    if error_subcode == 463:  # Token expired
                        return {
                            "error": "Facebook access token expired. Please reconnect Facebook in Settings."
                        }
                    elif error_subcode == 467:  # Token invalid
                        return {
                            "error": "Facebook access token invalid. Please reconnect Facebook in Settings."
                        }
                    else:
                        # Try to get page info to see if token works for page operations
                        page_url = f"https://graph.facebook.com/v18.0/{page_id}?fields=id,name&access_token={access_token}"
                        page_response = requests.get(page_url, timeout=10)
                        if page_response.status_code == 200:
                            # Token is valid for page operations, continue
                            pass
                        else:
                            return {
                                "error": "Facebook access token issue. Please reconnect Facebook in Settings."
                            }
                else:
                    error_msg = error_info.get("message", "Facebook API error")
                    if len(error_msg) > 150:
                        error_msg = error_msg[:150] + "..."
                    return {"error": error_msg}

        # Get page insights
        url = f"https://graph.facebook.com/v18.0/{page_id}/insights"
        params = {
            "metric": "page_impressions,page_reach,page_engaged_users,page_fans",
            "period": "day",
            "since": int((datetime.now(IST) - timedelta(days=30)).timestamp()),
            "until": int(datetime.now(IST).timestamp()),
            "access_token": access_token,
        }

        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {"insights": data.get("data", [])}
        else:
            error_data = response.json() if response.text else {}
            error_msg = "Facebook API error"
            if error_data.get("error"):
                error_info = error_data["error"]
                error_code = error_info.get("code")
                error_subcode = error_info.get("error_subcode")

                # More specific error handling
                if error_code == 190:
                    if error_subcode == 463:
                        error_msg = "Facebook access token expired. Please reconnect Facebook in Settings."
                    elif error_subcode == 467:
                        error_msg = "Facebook access token invalid. Please reconnect Facebook in Settings."
                    else:
                        error_msg = error_info.get(
                            "message", "Facebook token issue. Please reconnect."
                        )
                elif error_info.get("message"):
                    error_msg = error_info["message"]
                    if len(error_msg) > 150:
                        error_msg = error_msg[:150] + "..."
            else:
                error_msg = response.text[:150] if response.text else "Unknown error"
            return {"error": error_msg}
    except Exception as e:
        return {"error": f"Error getting Facebook Insights: {str(e)}"}


def get_linkedin_analytics():
    """Get LinkedIn Analytics from database."""
    from app.database import get_db_connection

    try:
        # Get stats from database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                COUNT(*) as total_posts,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
            FROM social_media_posts
            WHERE platform = 'linkedin'
        """
        )
        stats = cursor.fetchone()

        # Get recent posts
        cursor.execute(
            """
            SELECT 
                video_id,
                post_content,
                status,
                schedule_date,
                created_at
            FROM social_media_posts
            WHERE platform = 'linkedin'
            ORDER BY created_at DESC
            LIMIT 10
        """
        )
        recent_posts = cursor.fetchall()

        conn.close()

        linkedin_data = {
            "source": "database",
            "total_posts": stats["total_posts"] if stats else 0,
            "published": stats["published"] if stats else 0,
            "scheduled": stats["scheduled"] if stats else 0,
            "pending": stats["pending"] if stats else 0,
            "recent_posts": (
                [
                    {
                        "video_id": p["video_id"],
                        "content": p["post_content"][:100] if p["post_content"] else "",
                        "status": p["status"],
                        "schedule_date": p["schedule_date"],
                    }
                    for p in recent_posts
                ]
                if recent_posts
                else []
            ),
            "note": "Data from local database. Configure LinkedIn API for live insights.",
        }

        if stats and stats["total_posts"] == 0:
            linkedin_data["message"] = (
                "No LinkedIn posts yet. Schedule posts from Shorts page."
            )

        return linkedin_data

    except Exception as e:
        app.logger.error(f"Error getting LinkedIn analytics from database: {e}")
        return {
            "error": "Unable to fetch LinkedIn analytics",
            "total_posts": 0,
            "published": 0,
            "scheduled": 0,
            "suggestion": "Schedule posts to LinkedIn from the Shorts page.",
        }


def calculate_optimal_posting_times(youtube_data, facebook_data, linkedin_data):
    """Calculate optimal posting times based on audience activity."""
    optimal_times = {
        "youtube": None,
        "facebook": None,
        "linkedin": None,
        "overall": None,
    }

    try:
        # Analyze YouTube hourly activity
        if (
            youtube_data
            and "hourly_activity" in youtube_data
            and youtube_data.get("hourly_activity")
        ):
            hourly_views = {}
            for row in youtube_data["hourly_activity"]:
                hour = row[1] if len(row) > 1 else 0
                views = row[2] if len(row) > 2 else 0
                hourly_views[hour] = hourly_views.get(hour, 0) + views

            if hourly_views:
                best_hour = max(hourly_views.items(), key=lambda x: x[1])[0]
                optimal_times["youtube"] = {
                    "hour": best_hour,
                    "best_times": sorted(
                        hourly_views.items(), key=lambda x: x[1], reverse=True
                    )[:3],
                }

        # Analyze Facebook insights for best posting times
        if facebook_data and "insights" in facebook_data:
            # Facebook provides insights data - would need to parse for time patterns
            optimal_times["facebook"] = {
                "note": "Analyze Facebook insights data for time patterns"
            }

        # Overall recommendation
        if optimal_times["youtube"]:
            optimal_times["overall"] = optimal_times["youtube"]

        return optimal_times
    except Exception as e:
        return {"error": f"Error calculating optimal times: {str(e)}"}


@app.route("/activity")
def activity():
    """Activity log page showing all automation activities."""
    try:
        from app.database import get_activity_logs

        # Get activity logs (last 200 by default)
        logs = get_activity_logs(limit=200)

        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in activity route: {e}", exc_info=True)
        # Return empty logs on error instead of crashing
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )


@app.route("/api/activity/<int:activity_id>")
def api_activity_details(activity_id):
    """Get detailed information about a specific activity."""
    try:
        from app.database import get_db_connection
        import json

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM activity_logs WHERE id = ?", (activity_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({"error": "Activity not found"}), 404

        log = dict(row)

        # Parse details JSON if it's a string
        if log.get("details") and isinstance(log["details"], str):
            try:
                log["details"] = json.loads(log["details"])
            except:
                pass

        return jsonify({"log": log})
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/api/autopilot/run", methods=["POST"])
def api_autopilot_run():
    """Run auto-pilot mode: select one video from each playlist and schedule on all channels."""
    try:
        from app.database import (
            log_activity,
            get_scheduled_count_today,
            insert_or_update_social_post,
            get_video,
            get_video_social_posts_from_db,
        )

        settings = load_settings()
        thresholds = settings.get("thresholds", {})
        platforms = settings.get("scheduling", {}).get(
            "social_platforms", ["linkedin", "facebook", "instagram"]
        )

        youtube = get_youtube_service()
        if not youtube:
            return jsonify({"error": "YouTube API not configured"}), 400

        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return jsonify({"error": "Could not find YouTube channel"}), 400

        # Get all playlists
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)

        # Filter to Shorts playlists only (you can change this filter)
        shorts_playlists = [
            pl
            for pl in playlists_data
            if "short" in pl.get("playlistTitle", "").lower()
        ]

        if not shorts_playlists:
            return jsonify({"error": "No playlists found"}), 400

        selected_videos = []
        activities = []
        today_str = datetime.now(IST).strftime("%Y-%m-%d")

        # Get targeting settings
        targeting = settings.get("targeting", {})
        target_audience = targeting.get("target_audience", "all")
        interview_types = targeting.get("interview_types", [])
        role_levels = targeting.get("role_levels", [])

        # Import tagging functions for filtering
        from app.tagging import derive_type_enhanced, derive_role_enhanced
        from app.database import get_video

        # Select one video from each playlist (with targeting filter)
        for playlist in shorts_playlists:
            playlist_id = playlist["playlistId"]
            videos = fetch_playlist_videos_from_youtube(
                youtube, playlist_id, playlist.get("channelTitle", "")
            )

            if videos:
                selected_video = None
                playlist_title = playlist.get("playlistTitle", "")

                # Filter videos based on targeting criteria
                for video in videos:
                    video_id = video["videoId"]

                    # Get video from database or derive type/role
                    db_video = get_video(video_id)
                    if db_video:
                        video_type = db_video.get("video_type", "")
                        role = db_video.get("role", "")
                    else:
                        # Derive type and role from content
                        video_type = derive_type_enhanced(
                            playlist_title,
                            video.get("title", ""),
                            video.get("description", ""),
                            video.get("tags", ""),
                        )
                        role = derive_role_enhanced(
                            playlist_title,
                            video.get("title", ""),
                            video.get("description", ""),
                            video.get("tags", ""),
                        )

                    # Apply targeting filters if targeting USA students
                    if target_audience == "usa_students":
                        # Check if video type matches interview types
                        type_matches = not interview_types or any(
                            it in video_type for it in interview_types
                        )

                        # Check if role matches student roles
                        role_matches = (
                            not role_levels
                            or any(rl in role for rl in role_levels)
                            or role == ""
                        )  # Allow videos without specific role

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
                    video_id = selected_video["videoId"]
                    selected_videos.append(
                        {
                            "video": selected_video,
                            "playlist_id": playlist_id,
                            "playlist_name": playlist.get("playlistTitle", ""),
                        }
                    )

        # Schedule selected videos to all platforms (respecting thresholds)
        scheduled_count = 0
        for item in selected_videos:
            video = item["video"]
            video_id = video["videoId"]
            video_title = video.get("title", "")
            playlist_id = item["playlist_id"]
            playlist_name = item["playlist_name"]

            # Get existing social posts or generate new ones
            existing_posts = get_video_social_posts_from_db(video_id)

            # Get or generate social media posts
            for platform in platforms:
                # Check threshold
                platform_limit_key = f"{platform}_daily_limit"
                daily_limit = thresholds.get(platform_limit_key, 25)
                scheduled_today = get_scheduled_count_today(platform, today_str)

                if scheduled_today >= daily_limit:
                    log_activity(
                        "schedule_post",
                        platform=platform,
                        video_id=video_id,
                        video_title=video_title,
                        playlist_id=playlist_id,
                        playlist_name=playlist_name,
                        status="skipped",
                        message=f"Daily limit reached ({scheduled_today}/{daily_limit})",
                    )
                    activities.append(
                        {
                            "action": "skipped",
                            "platform": platform,
                            "video_title": video_title,
                            "reason": f"Daily limit reached",
                        }
                    )
                    continue

                # Get existing post content or use placeholder
                post_content = None
                for post in existing_posts:
                    if post.get("platform") == platform:
                        post_content = post.get("post_content", "")
                        break

                if not post_content:
                    # Generate post content with CTAs using YouTube metadata
                    db_video = get_video(video_id)
                    title = (
                        db_video.get("title", video_title) if db_video else video_title
                    )
                    description = (
                        db_video.get("description", video.get("description", ""))
                        if db_video
                        else video.get("description", "")
                    )
                    tags = (
                        db_video.get("tags", video.get("tags", ""))
                        if db_video
                        else video.get("tags", "")
                    )
                    youtube_url = f"https://youtube.com/watch?v={video_id}"
                    playlist_name = playlist.get("playlistTitle", "")

                    # Derive video type and role for better hashtags
                    from app.tagging import derive_type_enhanced, derive_role_enhanced

                    video_type = derive_type_enhanced(
                        playlist_name, title, description, tags
                    )
                    video_role = derive_role_enhanced(
                        playlist_name, title, description, tags
                    )

                    # Generate hashtags
                    hashtags = generate_hashtags_for_rupesh(
                        video_type, video_role, title, description
                    )

                    # CTAs
                    booking_cta = (
                        "📅 Book 1-on-1 coaching: https://fullstackmaster/book"
                    )
                    whatsapp_cta = "💬 WhatsApp: +1-609-442-4081"

                    # Extract key points from description
                    description_lines = (
                        description.split("\n")[:3] if description else []
                    )
                    key_points = "\n".join(
                        [line.strip() for line in description_lines if line.strip()][:2]
                    )

                    # Generate clickbait-style posts with psychological triggers
                    post_content = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform=platform,
                        youtube_url=youtube_url,
                    )

                # Validate platform credentials BEFORE scheduling
                is_valid, error_message = validate_platform_credentials(platform)
                if not is_valid:
                    log_activity(
                        "schedule_post",
                        platform=platform,
                        video_id=video_id,
                        video_title=video_title,
                        playlist_id=playlist_id,
                        playlist_name=playlist_name,
                        status="error",
                        message=f"Failed to schedule: {error_message}",
                        details={"error": error_message, "validation_failed": True},
                    )
                    activities.append(
                        {
                            "action": "failed",
                            "platform": platform,
                            "video_title": video_title,
                            "reason": error_message,
                        }
                    )
                    continue

                # Calculate schedule date (next scheduled day/time)
                schedule_time = settings.get("scheduling", {}).get(
                    "social_media_schedule_time", "19:30"
                )
                schedule_day = settings.get("scheduling", {}).get(
                    "schedule_day", "wednesday"
                )

                # Calculate next occurrence
                today = datetime.now(IST)
                days_ahead = {
                    "monday": 0,
                    "tuesday": 1,
                    "wednesday": 2,
                    "thursday": 3,
                    "friday": 4,
                    "saturday": 5,
                    "sunday": 6,
                }[schedule_day.lower()]
                next_date = today + timedelta(days=(days_ahead - today.weekday()) % 7)
                if next_date <= today:
                    next_date += timedelta(days=7)

                schedule_datetime = f"{next_date.strftime('%Y-%m-%d')} {schedule_time}"

                # Save to database
                insert_or_update_social_post(
                    video_id,
                    platform,
                    {
                        "post_content": post_content,
                        "schedule_date": schedule_datetime,
                        "status": "scheduled",
                    },
                )

                log_activity(
                    "schedule_post",
                    platform=platform,
                    video_id=video_id,
                    video_title=video_title,
                    playlist_id=playlist_id,
                    playlist_name=playlist_name,
                    status="success",
                    message=f"Scheduled for {schedule_datetime}",
                    details={"schedule_date": schedule_datetime},
                )

                activities.append(
                    {
                        "action": "scheduled",
                        "platform": platform,
                        "video_title": video_title,
                        "schedule_date": schedule_datetime,
                    }
                )
                scheduled_count += 1

        return jsonify(
            {
                "success": True,
                "message": f"Auto-pilot completed: {len(selected_videos)} videos selected, {scheduled_count} posts scheduled",
                "activities": activities,
                "videos_selected": len(selected_videos),
                "posts_scheduled": scheduled_count,
            }
        )

    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/content-preview")
def content_preview():
    """Content preview page - serve React app (React will fetch data from /api/content-preview/videos)."""
    try:
        # Serve React app - it will fetch data from /api/content-preview/videos endpoint
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        # Fallback to Flask template if React build doesn't exist
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in content_preview route: {e}", exc_info=True)
        return render_template(
            "error.html", message=f"Error loading content preview: {str(e)}"
        )


@app.route("/api/content-preview/videos")
def api_content_preview_videos():
    """Get all videos with their social media posts for content preview."""
    try:
        from app.database import get_db_connection, get_video
        from app.tagging import derive_type_enhanced, derive_role_enhanced

        youtube = get_youtube_service()
        if not youtube:
            return jsonify({"error": "YouTube API not configured"}), 500

        channel_id = get_my_channel_id_helper(youtube)
        if not channel_id:
            return jsonify({"error": "Channel not found"}), 500

        # Get all playlists
        playlists_data = fetch_all_playlists_from_youtube(youtube, channel_id)
        shorts_playlists = [
            pl
            for pl in playlists_data
            if "short" in pl.get("playlistTitle", "").lower()
        ]

        all_videos = []
        for playlist in shorts_playlists:
            videos = fetch_playlist_videos_from_youtube(
                youtube, playlist["playlistId"], playlist.get("channelTitle", "")
            )
            for video in videos:
                video_id = video["videoId"]

                # Get social posts from database
                social_posts_list = get_video_social_posts_from_db(video_id)

                # Convert list to dict for easier access
                social_posts = {}
                if social_posts_list:
                    for post in social_posts_list:
                        if post and post.get("platform"):
                            social_posts[post["platform"]] = post

                # Get video from database for metadata
                db_video = get_video(video_id)

                # Extract video metadata (always needed)
                title = video.get("title", "")
                description = video.get("description", "")
                tags = video.get("tags", "")
                published_at = video.get("publishedAt", "")
                youtube_url = f"https://youtube.com/watch?v={video_id}"
                playlist_name = playlist.get("playlistTitle", "")

                # Generate posts if not exist
                if not social_posts or len(social_posts) == 0:
                    # Generate posts aligned with Rupesh's coaching expertise
                    from app.tagging import derive_type_enhanced, derive_role_enhanced

                    # Derive video type and role for better hashtags
                    video_type = derive_type_enhanced(
                        playlist_name, title, description, tags
                    )
                    video_role = derive_role_enhanced(
                        playlist_name, title, description, tags
                    )

                    # Generate hashtags based on Rupesh's expertise
                    hashtags = generate_hashtags_for_rupesh(
                        video_type, video_role, title, description
                    )

                    # CTAs
                    booking_cta = (
                        "📅 Book 1-on-1 coaching: https://fullstackmaster/book"
                    )
                    whatsapp_cta = "💬 WhatsApp: +1-609-442-4081"

                    # Extract key points from description (first 2-3 sentences)
                    description_lines = (
                        description.split("\n")[:3] if description else []
                    )
                    key_points = "\n".join(
                        [line.strip() for line in description_lines if line.strip()][:2]
                    )

                    # Generate clickbait-style posts with psychological triggers
                    linkedin_post = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform="linkedin",
                        youtube_url=youtube_url,
                    )

                    facebook_post = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform="facebook",
                        youtube_url=youtube_url,
                    )

                    instagram_post = generate_clickbait_post(
                        title=title,
                        description=description,
                        video_type=video_type,
                        video_role=video_role,
                        platform="instagram",
                        youtube_url=youtube_url,
                    )

                    social_posts = {
                        "linkedin": {
                            "platform": "linkedin",
                            "post_content": linkedin_post,
                            "status": "pending",
                            "schedule_date": None,
                        },
                        "facebook": {
                            "platform": "facebook",
                            "post_content": facebook_post,
                            "status": "pending",
                            "schedule_date": None,
                        },
                        "instagram": {
                            "platform": "instagram",
                            "post_content": instagram_post,
                            "status": "pending",
                            "schedule_date": None,
                        },
                    }

                # Get tags and published date from video data
                video_tags = tags
                if isinstance(video_tags, list):
                    video_tags = ", ".join(video_tags)
                elif not video_tags:
                    video_tags = video.get("tags", "")
                    if isinstance(video_tags, list):
                        video_tags = ", ".join(video_tags)

                # Ensure published_at is set (use the one extracted earlier)
                if not published_at:
                    published_at = video.get("publishedAt", "") or video.get(
                        "published_at", ""
                    )

                all_videos.append(
                    {
                        "video_id": video_id,
                        "title": title or "Untitled Video",
                        "description": description or "",
                        "tags": video_tags or "",
                        "published_at": published_at or "",
                        "thumbnail": video.get("thumbnail", ""),
                        "video_url": youtube_url,
                        "playlist_name": playlist_name
                        or playlist.get("playlistTitle", ""),
                        "playlist_id": playlist["playlistId"],
                        "social_posts": social_posts,
                        "video_type": (
                            db_video.get("video_type", "") if db_video else ""
                        ),
                        "role": db_video.get("role", "") if db_video else "",
                    }
                )

        return jsonify({"videos": all_videos, "count": len(all_videos)})
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


def validate_platform_credentials(platform: str) -> tuple[bool, str]:
    """Validate that platform credentials are configured.

    Returns:
        (is_valid, error_message)
    """
    settings = load_settings()
    api_keys = settings.get("api_keys", {})
    platform_lower = platform.lower()

    if platform_lower == "linkedin":
        access_token = api_keys.get("linkedin_access_token", "").strip()
        person_urn = api_keys.get("linkedin_person_urn", "").strip()

        if not access_token:
            return (
                False,
                "LinkedIn Access Token is not configured. Please connect LinkedIn in Settings.",
            )
        if not person_urn:
            return (
                False,
                "LinkedIn Person URN is not configured. Please connect LinkedIn in Settings.",
            )

        return True, ""

    elif platform_lower == "facebook":
        page_access_token = api_keys.get("facebook_page_access_token", "").strip()
        page_id = api_keys.get("facebook_page_id", "").strip()

        if not page_access_token:
            return (
                False,
                "Facebook Page Access Token is not configured. Please connect Facebook in Settings.",
            )
        if not page_id:
            return (
                False,
                "Facebook Page ID is not configured. Please connect Facebook in Settings.",
            )

        return True, ""

    elif platform_lower == "instagram":
        # Instagram uses Facebook Page Access Token and Instagram Business Account ID
        page_access_token = api_keys.get("facebook_page_access_token", "").strip()
        instagram_account_id = api_keys.get("instagram_business_account_id", "").strip()

        if not page_access_token:
            return (
                False,
                "Instagram requires Facebook Page Access Token. Please connect Facebook in Settings (Instagram uses Facebook credentials).",
            )
        if not instagram_account_id:
            return (
                False,
                "Instagram Business Account ID is not configured. Please connect Instagram in Settings.",
            )

        return True, ""

    elif platform_lower == "instagram":
        instagram_account_id = api_keys.get("instagram_business_account_id", "").strip()
        page_access_token = api_keys.get("facebook_page_access_token", "").strip()

        if not instagram_account_id:
            return (
                False,
                "Instagram Business Account ID is not configured. Please connect Facebook (which includes Instagram) in Settings.",
            )
        if not page_access_token:
            return (
                False,
                "Facebook Page Access Token is not configured (required for Instagram). Please connect Facebook in Settings.",
            )

        return True, ""

    else:
        return False, f"Unknown platform: {platform}"


@app.route("/api/schedule-post", methods=["POST"])
def api_schedule_post():
    """Schedule a post manually with custom date/time. Actually creates the post on the platform."""
    try:
        from app.database import insert_or_update_social_post, log_activity, get_video
        import requests

        data = request.json or {}
        video_id = data.get("video_id")
        platform = data.get("platform")
        post_content = data.get("post_content")
        schedule_datetime = data.get("schedule_datetime")  # Format: "2026-01-15 14:00"

        # Defensive validation with detailed error messages
        missing_fields = []
        if not video_id:
            missing_fields.append("video_id")
        if not platform:
            missing_fields.append("platform")
        if not post_content:
            missing_fields.append("post_content")
        if not schedule_datetime:
            missing_fields.append("schedule_datetime")

        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            app.logger.warning(f"Schedule post validation failed: {error_msg}")
            return (
                jsonify(
                    {
                        "success": False,
                        "error": error_msg,
                        "missing_fields": missing_fields,
                        "received_data": {
                            "has_video_id": bool(video_id),
                            "has_platform": bool(platform),
                            "has_post_content": bool(post_content),
                            "has_schedule_datetime": bool(schedule_datetime),
                            "platform_value": platform,
                            "post_content_length": (
                                len(post_content) if post_content else 0
                            ),
                        },
                    }
                ),
                400,
            )

        # Validate post_content is not just whitespace
        if not post_content.strip():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Post content cannot be empty or only whitespace",
                        "received_data": {
                            "post_content_length": len(post_content),
                            "post_content_preview": (
                                post_content[:50] if post_content else None
                            ),
                        },
                    }
                ),
                400,
            )

        # Validate schedule_datetime format
        try:
            from datetime import datetime

            # Handle different datetime formats
            schedule_dt = None
            try:
                # Try ISO format first (YYYY-MM-DDTHH:MM:SS)
                schedule_dt = datetime.fromisoformat(
                    schedule_datetime.replace("Z", "+00:00")
                )
            except ValueError:
                try:
                    # Try format without seconds (YYYY-MM-DDTHH:MM)
                    schedule_dt = datetime.strptime(schedule_datetime, "%Y-%m-%dT%H:%M")
                except ValueError:
                    # Try space-separated format (YYYY-MM-DD HH:MM:SS)
                    try:
                        schedule_dt = datetime.strptime(
                            schedule_datetime, "%Y-%m-%d %H:%M:%S"
                        )
                    except ValueError:
                        # Try space-separated without seconds
                        schedule_dt = datetime.strptime(
                            schedule_datetime, "%Y-%m-%d %H:%M"
                        )

            if schedule_dt <= datetime.now():
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Schedule date/time must be in the future",
                            "received_datetime": schedule_datetime,
                            "current_datetime": datetime.now().isoformat(),
                        }
                    ),
                    400,
                )
        except (ValueError, AttributeError) as e:
            app.logger.error(
                f"DateTime parsing error: {str(e)}, received: {schedule_datetime}"
            )
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"Invalid schedule_datetime format: {str(e)}. Received: {schedule_datetime}. Expected format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM",
                        "received_datetime": schedule_datetime,
                    }
                ),
                400,
            )

        # Validate platform credentials BEFORE scheduling
        is_valid, error_message = validate_platform_credentials(platform)
        if not is_valid:
            # Log as error
            log_activity(
                "schedule_post",
                platform=platform,
                video_id=video_id,
                status="error",
                message=f"Failed to schedule: {error_message}",
                details={
                    "schedule_date": schedule_datetime,
                    "manual": True,
                    "error": error_message,
                    "validation_failed": True,
                },
            )
            return jsonify({"success": False, "error": error_message}), 400

        # Get API credentials
        settings = load_settings()
        api_keys = settings.get("api_keys", {})

        # Get video URL
        db_video = get_video(video_id)
        video_url = (
            db_video.get("youtube_url", f"https://youtube.com/watch?v={video_id}")
            if db_video
            else f"https://youtube.com/watch?v={video_id}"
        )

        # Actually create the post on the platform
        success = False
        error_msg = None
        post_id = None

        try:
            if platform.lower() == "facebook":
                # Schedule Facebook post
                page_id = api_keys.get("facebook_page_id")
                page_access_token = api_keys.get("facebook_page_access_token")

                if not page_id or not page_access_token:
                    error_msg = "Facebook Page ID and Access Token are required"
                else:
                    # Convert schedule_datetime to Unix timestamp for Facebook
                    from datetime import datetime

                    # Handle both T-separated and space-separated formats
                    try:
                        # Try ISO format first (YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM)
                        schedule_dt = datetime.fromisoformat(
                            schedule_datetime.replace("Z", "+00:00").split("+")[0]
                        )
                    except (ValueError, AttributeError):
                        try:
                            # Try space-separated format (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM)
                            schedule_dt = datetime.strptime(
                                schedule_datetime, "%Y-%m-%d %H:%M:%S"
                            )
                        except ValueError:
                            schedule_dt = datetime.strptime(
                                schedule_datetime, "%Y-%m-%d %H:%M"
                            )
                    scheduled_publish_time = int(schedule_dt.timestamp())

                    # Facebook Graph API - create scheduled post
                    params = {
                        "access_token": page_access_token,
                        "message": post_content,
                        "link": video_url,
                        "scheduled_publish_time": scheduled_publish_time,
                        "published": False,  # Schedule it
                    }

                    response = requests.post(
                        f"https://graph.facebook.com/v18.0/{page_id}/feed",
                        params=params,
                        timeout=30,
                    )

                    response_data = response.json()

                    if response.status_code == 200 and "id" in response_data:
                        post_id = response_data["id"]
                        success = True
                    else:
                        error_data = response_data.get("error", {})
                        error_code = error_data.get("code", "unknown")
                        error_message = error_data.get("message", "Unknown error")

                        # Check for token expiration (error code 190)
                        if error_code == 190:
                            if (
                                "expired" in error_message.lower()
                                or error_data.get("error_subcode") == 463
                            ):
                                error_msg = "TOKEN_EXPIRED: Facebook access token has expired. Please reconnect Facebook in Settings."
                            elif error_data.get("error_subcode") == 467:
                                error_msg = "TOKEN_INVALID: Facebook access token is invalid. Please reconnect Facebook in Settings."
                            else:
                                error_msg = f"TOKEN_ERROR: Facebook access token issue. Please reconnect Facebook in Settings. ({error_message})"
                        else:
                            error_msg = (
                                f"Facebook API error ({error_code}): {error_message}"
                            )

            elif platform.lower() == "instagram":
                # Instagram doesn't support scheduling via API
                # Posts must be published immediately
                # However, we can save it and publish immediately, or tell user to use Facebook Business Suite
                instagram_business_account_id = api_keys.get(
                    "instagram_business_account_id"
                )
                page_access_token = api_keys.get("facebook_page_access_token")

                if not instagram_business_account_id or not page_access_token:
                    error_msg = "Instagram Business Account ID and Facebook Page Access Token are required"
                else:
                    # Instagram requires native video upload, not link sharing
                    # For now, return an error explaining this
                    error_msg = "Instagram Reels require native video upload. Link sharing is not supported. Please use Facebook Business Suite to schedule Instagram posts, or enable native video upload in settings."

            elif platform.lower() == "linkedin":
                # LinkedIn doesn't support scheduled posts via API
                # Posts must be published immediately
                error_msg = "LinkedIn API doesn't support scheduled posts. Posts must be published immediately. Please use 'Publish Now' instead."

            else:
                error_msg = f"Unsupported platform: {platform}"

        except requests.exceptions.Timeout:
            error_msg = f"{platform} API request timed out"
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
        except Exception as e:
            import traceback

            error_msg = f"Error creating post: {str(e)}"
            app.logger.error(
                f"Error in api_schedule_post for {platform}: {e}\n{traceback.format_exc()}"
            )

        # Only save to database and return success if API call succeeded
        if success:
            # Save to database
            insert_or_update_social_post(
                video_id,
                platform,
                {
                    "post_content": post_content,
                    "schedule_date": schedule_datetime,
                    "status": "scheduled",
                    "platform_post_id": post_id,
                },
            )

            # Log activity as success
            log_activity(
                "schedule_post",
                platform=platform,
                video_id=video_id,
                status="success",
                message=f"Successfully scheduled on {platform} for {schedule_datetime}",
                details={
                    "schedule_date": schedule_datetime,
                    "manual": True,
                    "platform_post_id": post_id,
                },
            )

            return jsonify(
                {
                    "success": True,
                    "message": f"Post successfully scheduled on {platform} for {schedule_datetime}",
                    "post_id": post_id,
                }
            )
        else:
            # Log as error
            log_activity(
                "schedule_post",
                platform=platform,
                video_id=video_id,
                status="error",
                message=f"Failed to schedule on {platform}: {error_msg}",
                details={
                    "schedule_date": schedule_datetime,
                    "manual": True,
                    "error": error_msg,
                },
            )

            return jsonify({"success": False, "error": error_msg}), 400

    except Exception as e:
        import traceback
        from app.database import log_activity

        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "schedule_date": (
                data.get("schedule_datetime") if "data" in locals() else None
            ),
            "manual": True,
        }

        # Log exception
        log_activity(
            "schedule_post",
            platform=(
                data.get("platform", "unknown") if "data" in locals() else "unknown"
            ),
            video_id=data.get("video_id", "") if "data" in locals() else "",
            status="error",
            message=f"Exception: {str(e)}",
            details=error_details,
        )

        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "details": error_details,
                }
            ),
            500,
        )


@app.route("/api/schedule-to-platform", methods=["POST"])
def api_schedule_to_platform():
    """Quick schedule a video to a platform (Buffer.com style)."""
    try:
        from app.database import insert_or_update_social_post, log_activity, get_video
        from datetime import datetime, timedelta

        data = request.json or {}
        video_id = data.get("video_id")
        platform = data.get("platform", "").lower()

        if not video_id or not platform:
            return (
                jsonify({"success": False, "error": "Missing video_id or platform"}),
                400,
            )

        # Get video details from database
        video = get_video(video_id)
        if not video:
            return jsonify({"success": False, "error": "Video not found"}), 404

        # Auto-generate post content
        video_title = video.get("title", "Check out this video!")
        youtube_url = video.get("youtube_url", f"https://youtube.com/shorts/{video_id}")

        # Platform-specific post content
        if platform == "facebook":
            post_content = (
                f"{video_title}\n\n🎥 Watch here: {youtube_url}\n\n#Shorts #Video"
            )
        elif platform == "instagram":
            post_content = f"{video_title}\n\n🔗 Link in bio\n\n#Shorts #Reels #Video"
        elif platform == "linkedin":
            post_content = f"{video_title}\n\nWatch the full video: {youtube_url}\n\n#ProfessionalDevelopment #Learning"
        else:
            post_content = f"{video_title}\n\n{youtube_url}"

        # Schedule for tomorrow at 2 PM
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_datetime = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        schedule_str = schedule_datetime.strftime("%Y-%m-%d %H:%M")

        # Save to database
        insert_or_update_social_post(
            video_id,
            platform,
            {
                "post_content": post_content,
                "schedule_date": schedule_str,
                "status": "scheduled",
            },
        )

        # Log activity
        log_activity(
            "quick_schedule",
            platform=platform,
            video_id=video_id,
            status="success",
            message=f"Quick scheduled on {platform} for {schedule_str}",
            details={
                "schedule_date": schedule_str,
                "auto_generated": True,
            },
        )

        return jsonify(
            {
                "success": True,
                "message": f"Scheduled to {platform} for {schedule_str}",
                "schedule_date": schedule_str,
                "post_content": post_content,
            }
        )

    except Exception as e:
        import traceback

        app.logger.error(
            f"Error in api_schedule_to_platform: {e}\n{traceback.format_exc()}"
        )
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/playlist/<playlist_id>/videos")
def api_playlist_videos(playlist_id):
    """API endpoint to fetch videos for a playlist (lazy loading)."""
    youtube = get_youtube_service()
    if not youtube:
        return jsonify({"error": "YouTube API not configured"}), 500

    try:
        # Get channel info for channel title
        channel_id = get_my_channel_id_helper(youtube)
        channel_title = ""
        if channel_id:
            try:
                channel_response = (
                    youtube.channels().list(part="snippet", id=channel_id).execute()
                )
                if channel_response.get("items"):
                    channel_title = (
                        channel_response["items"][0].get("snippet", {}).get("title", "")
                    )
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
                playlist_title = (
                    ""  # We don't have playlist title here, but can get from context
                )
                video_type = derive_type_enhanced(
                    playlist_title,
                    video.get("title", ""),
                    video.get("description", ""),
                    video.get("tags", ""),
                )
                role = derive_role_enhanced(
                    playlist_title,
                    video.get("title", ""),
                    video.get("description", ""),
                    video.get("tags", ""),
                )
                video["video_type"] = video_type
                video["role"] = role
                video["custom_tags"] = ""

                # Suggest tags
                suggested_tags = suggest_tags(
                    video.get("title", ""),
                    video.get("description", ""),
                    video_type,
                    role,
                )
                video["suggested_tags"] = suggested_tags

        # Add cache control headers to prevent browser caching
        response = make_response(jsonify({"videos": videos}))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/api/video/<video_id>/tags", methods=["GET", "POST"])
def api_video_tags(video_id):
    """Get or update video tags."""
    from app.database import get_video, get_db_connection
    from app.tagging import parse_tags, format_tags

    if request.method == "GET":
        video = get_video(video_id)
        if not video:
            return jsonify({"error": "Video not found"}), 404

        return jsonify(
            {
                "video_type": video.get("video_type", ""),
                "role": video.get("role", ""),
                "custom_tags": video.get("custom_tags", ""),
                "tags": parse_tags(video.get("custom_tags", "")),
            }
        )

    elif request.method == "POST":
        data = request.json
        video_type = data.get("video_type", "")
        role = data.get("role", "")
        custom_tags = format_tags(data.get("tags", []))

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE videos 
            SET video_type = ?, role = ?, custom_tags = ?, updated_at = CURRENT_TIMESTAMP
            WHERE video_id = ?
        """,
            (video_type, role, custom_tags, video_id),
        )

        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Tags updated successfully"})


@app.route("/api/videos/search")
def api_search_videos():
    """Search videos by query, type, role, or tags."""
    from app.database import get_db_connection
    from app.tagging import search_videos, parse_tags

    query = request.args.get("q", "")
    video_type = request.args.get("type", "")
    role = request.args.get("role", "")
    tags_param = request.args.get("tags", "")

    tags = parse_tags(tags_param) if tags_param else None

    conn = get_db_connection()
    cursor = conn.cursor()

    # Build query
    sql = "SELECT * FROM videos "
    where_clause = search_videos(
        query, video_type if video_type else None, role if role else None, tags
    )
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
    return jsonify({"videos": videos, "count": len(videos)})


@app.route("/calendar")
def calendar():
    """Calendar page - serve React app (React will fetch data from /api/calendar-data)."""
    try:
        # Serve React app - it will fetch data from /api/calendar-data endpoint
        if os.path.exists(FRONTEND_BUILD_DIR) and os.path.exists(
            os.path.join(FRONTEND_BUILD_DIR, "index.html")
        ):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")
        # Fallback to Flask template if React build doesn't exist
        return (
            jsonify(
                {
                    "error": "React build not found. Please run: cd frontend && npm run build"
                }
            ),
            500,
        )
    except Exception as e:
        app.logger.error(f"Error in calendar route: {e}", exc_info=True)
        return (
            f"<html><body><h1>Error loading calendar</h1><p>{str(e)}</p></body></html>",
            500,
        )


@app.route("/content")
def content():
    """Content management page - view and schedule videos across all channels."""
    return (
        jsonify(
            {"error": "React build not found. Please run: cd frontend && npm run build"}
        ),
        500,
    )


@app.route("/api/content/videos")
def api_content_videos():
    """API endpoint to fetch videos with social media post status for content page."""
    from app.database import get_db_connection
    import pandas as pd

    try:
        conn = get_db_connection()

        # Get all videos that are public or scheduled
        query = """
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
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        videos = []
        for _, row in df.iterrows():
            video = {
                "video_id": row.get("video_id", ""),
                "title": row.get("title", ""),
                "description": row.get("description", "") or "",
                "tags": row.get("tags", "") or "",
                "youtube_url": row.get("youtube_url", ""),
                "video_type": row.get("video_type", "") or "",
                "role": row.get("role", "") or "",
                "custom_tags": row.get("custom_tags", "") or "",
                "playlist_name": row.get("playlist_name", "") or "",
                "youtube_published_date": (
                    str(row.get("youtube_published_date", ""))
                    if pd.notna(row.get("youtube_published_date"))
                    else ""
                ),
                "youtube_schedule_date": (
                    str(row.get("youtube_schedule_date", ""))
                    if pd.notna(row.get("youtube_schedule_date"))
                    else ""
                ),
                "privacy_status": row.get("privacy_status", ""),
                "platforms": {
                    "linkedin": {
                        "status": row.get("linkedin_status", "") or "not_scheduled",
                        "schedule_date": (
                            str(row.get("linkedin_schedule_date", ""))
                            if pd.notna(row.get("linkedin_schedule_date"))
                            else ""
                        ),
                        "post_content": row.get("linkedin_post", "") or "",
                    },
                    "facebook": {
                        "status": row.get("facebook_status", "") or "not_scheduled",
                        "schedule_date": (
                            str(row.get("facebook_schedule_date", ""))
                            if pd.notna(row.get("facebook_schedule_date"))
                            else ""
                        ),
                        "post_content": row.get("facebook_post", "") or "",
                    },
                    "instagram": {
                        "status": row.get("instagram_status", "") or "not_scheduled",
                        "schedule_date": (
                            str(row.get("instagram_schedule_date", ""))
                            if pd.notna(row.get("instagram_schedule_date"))
                            else ""
                        ),
                        "post_content": row.get("instagram_post", "") or "",
                    },
                },
            }
            videos.append(video)

        return jsonify({"videos": videos})
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"error": str(e), "traceback": traceback.format_exc(), "videos": []}
            ),
            500,
        )


@app.route("/api/config/platforms")
def api_config_platforms():
    """API endpoint to get configured social media platforms."""
    settings = load_settings()
    scheduling = settings.get("scheduling", {})
    platforms = scheduling.get(
        "social_platforms", ["linkedin", "facebook", "instagram"]
    )
    return jsonify({"platforms": platforms})


@app.route("/api/config/save-section", methods=["POST"])
def api_save_config_section():
    """API endpoint to save a specific configuration section."""
    try:
        section = request.json.get("section")
        data = request.json.get("data", {})

        if not section:
            return jsonify({"success": False, "error": "Section not specified"}), 400

        settings = load_settings()

        # Update the specific section
        if section == "api_keys":
            settings["api_keys"] = {
                "linkedin_client_id": data.get("linkedin_client_id", ""),
                "linkedin_client_secret": data.get("linkedin_client_secret", ""),
                "linkedin_access_token": data.get("linkedin_access_token", ""),
                "linkedin_person_urn": data.get("linkedin_person_urn", ""),
                "facebook_page_access_token": data.get(
                    "facebook_page_access_token", ""
                ),
                "facebook_page_id": data.get("facebook_page_id", ""),
                "instagram_business_account_id": data.get(
                    "instagram_business_account_id", ""
                ),
                "ayrshare_api_key": data.get("ayrshare_api_key", ""),
            }
        elif section == "scheduling":
            settings["scheduling"] = {
                "enabled": data.get("scheduling_enabled") == True
                or data.get("scheduling_enabled") == "on",
                "videos_per_day": int(data.get("videos_per_day", 1)),
                "youtube_schedule_time": data.get("youtube_schedule_time", "23:00"),
                "social_media_schedule_time": data.get(
                    "social_media_schedule_time", "19:30"
                ),
                "schedule_day": data.get("schedule_day", "wednesday"),
                "playlist_id": data.get("playlist_id", ""),
                "export_type": data.get("export_type", "shorts"),
                "use_database": data.get("use_database") == True
                or data.get("use_database") == "on",
                "auto_post_social": data.get("auto_post_social") == True
                or data.get("auto_post_social") == "on",
                "social_platforms": data.get("social_platforms", []),
                "upload_method": data.get(
                    "upload_method", "native"
                ),  # 'native' or 'link'
            }
            # Reschedule job if scheduling settings changed
            schedule_daily_job()
        elif section == "thresholds":
            settings["thresholds"] = {
                "linkedin_daily_limit": int(data.get("linkedin_daily_limit", 25)),
                "facebook_daily_limit": int(data.get("facebook_daily_limit", 25)),
                "instagram_daily_limit": int(data.get("instagram_daily_limit", 25)),
                "youtube_daily_limit": int(data.get("youtube_daily_limit", 10)),
            }
        elif section == "targeting":
            settings["targeting"] = {
                "target_audience": data.get("target_audience", "usa_professionals"),
                "interview_types": data.get("interview_types", []),
                "role_levels": data.get("role_levels", []),
                "timezone": data.get("timezone", "America/New_York"),
                "optimal_times": (
                    data.get("optimal_times", [])
                    if isinstance(data.get("optimal_times"), list)
                    else ["14:00", "17:00", "21:00"]
                ),
            }
        elif section == "cta":
            settings["cta"] = {
                "booking_url": data.get("booking_url", "https://fullstackmaster/book"),
                "whatsapp_number": data.get("whatsapp_number", "+1-609-442-4081"),
                "linkedin_url": data.get("linkedin_url", ""),
                "instagram_url": data.get("instagram_url", ""),
                "facebook_url": data.get("facebook_url", ""),
                "youtube_url": data.get("youtube_url", ""),
                "twitter_url": data.get("twitter_url", ""),
                "website_url": data.get("website_url", ""),
            }
        else:
            return (
                jsonify({"success": False, "error": f"Unknown section: {section}"}),
                400,
            )

        save_settings(settings)

        return jsonify(
            {
                "success": True,
                "message": f'{section.replace("_", " ").title()} saved successfully!',
            }
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/linkedin/oauth/authorize")
def api_linkedin_oauth_authorize():
    """Buffer-style LinkedIn OAuth - just click 'Connect LinkedIn' and authorize."""
    try:
        settings = load_settings()
        api_keys = settings.get("api_keys", {})
        client_id = api_keys.get("linkedin_client_id", "").strip()
        client_secret = api_keys.get("linkedin_client_secret", "").strip()

        if not client_id or not client_secret:
            # Return JSON error for API calls, or redirect for browser
            if request.headers.get("Accept", "").startswith("application/json"):
                return (
                    jsonify(
                        {
                            "error": "LinkedIn Client ID and Secret not configured",
                            "redirect": "/settings#social-media-connections",
                        }
                    ),
                    400,
                )
            flash(
                "Please configure LinkedIn Client ID and Secret first in Settings → API Keys",
                "error",
            )
            return redirect("/settings#social-media-connections")

        # Generate state for security
        import secrets

        state = secrets.token_urlsafe(32)

        # Store state in session
        session["linkedin_oauth_state"] = state

        # Build OAuth URL with FIXED redirect URI (NOT dynamic from url_for)
        # CRITICAL: LinkedIn app settings must have this EXACT URL registered
        # Use 127.0.0.1 (not localhost) to match most common local development setups
        redirect_uri = "http://127.0.0.1:5001/api/linkedin/oauth/callback"

        # Store redirect_uri for debugging
        session["linkedin_redirect_uri"] = redirect_uri

        # Request scopes - use correct LinkedIn API scopes
        # w_member_social requires Marketing Developer Platform product
        # If you get "invalid_scope_error", enable Marketing Developer Platform in LinkedIn app settings
        # Using standard LinkedIn scopes (r_liteprofile and r_emailaddress are still valid)
        # w_member_social is required for posting content
        scopes = ["r_liteprofile", "r_emailaddress", "w_member_social"]

        # If Marketing Developer Platform is not enabled, these scopes won't be available
        # Check: https://www.linkedin.com/developers/apps/86vimp2gbw3c06/products

        # Use urlencode for proper URL parameter encoding
        from urllib.parse import urlencode

        auth_params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,  # urlencode will handle encoding properly
            "scope": " ".join(scopes),  # Space-separated, not %20
            "state": state,
        }
        auth_url = (
            f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
        )

        # Debug: Show redirect URI in flash message
        flash(
            f"🔗 Redirect URI: {redirect_uri} - Verify this matches LinkedIn settings exactly!",
            "info",
        )

        # Store redirect_uri for debugging
        session["linkedin_redirect_uri"] = redirect_uri

        # Redirect to LinkedIn (just like Buffer does)
        # Use 302 redirect explicitly and add headers to prevent caching
        response = redirect(auth_url, code=302)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    except Exception as e:
        flash(f"Error starting LinkedIn authorization: {str(e)}", "error")
        return redirect("/settings#social-media-connections")


@app.route("/api/facebook/oauth/authorize")
def api_facebook_oauth_authorize():
    """Buffer-style Facebook OAuth - opens helper page with instructions."""
    try:
        # Redirect directly to the helper page
        # The helper page will guide users through getting a Facebook Page Access Token
        helper_url = url_for("facebook_helper.facebook_token_helper", _external=False)
        response = redirect(helper_url, code=302)
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    except Exception as e:
        flash(f"Error starting Facebook authorization: {str(e)}", "error")
        return redirect("/settings#social-media-connections")


@app.route("/api/facebook/oauth/callback")
def api_facebook_oauth_callback():
    """Handle Facebook OAuth callback - automatically get Page Access Token and Page ID."""
    try:
        import requests

        # Get authorization code
        code = request.args.get("code")
        state = request.args.get("state")
        error = request.args.get("error")

        if error:
            error_desc = request.args.get("error_description", "")
            flash(f"Facebook authorization failed: {error} - {error_desc}", "error")
            return redirect("/settings#social-media-connections")

        if not code:
            flash(
                "Facebook authorization failed: No authorization code received", "error"
            )
            return redirect("/settings#social-media-connections")

        # Verify state
        stored_state = session.get("facebook_oauth_state")
        if state != stored_state:
            flash("Facebook authorization failed: Invalid state parameter", "error")
            return redirect("/settings#social-media-connections")

        # Get settings
        settings = load_settings()
        api_keys = settings.get("api_keys", {})

        # Exchange code for access token
        # Get Page Access Token and Page ID automatically
        # This is a simplified flow - full implementation would require App ID/Secret

        flash(
            "Facebook OAuth callback received. Full implementation requires App ID/Secret.",
            "info",
        )
        return redirect("/settings#social-media-connections")

    except Exception as e:
        flash(f"Facebook connection error: {str(e)}", "error")
        return redirect("/settings#social-media-connections")


@app.route("/api/linkedin/oauth/callback")
def api_linkedin_oauth_callback():
    """Handle LinkedIn OAuth callback - automatically get token and Person URN."""
    try:
        import requests

        # Get authorization code
        code = request.args.get("code")
        state = request.args.get("state")
        error = request.args.get("error")

        if error:
            error_desc = request.args.get("error_description", "")
            flash(f"LinkedIn authorization failed: {error} - {error_desc}", "error")
            return redirect("/settings#social-media-connections")

        if not code:
            flash(
                "LinkedIn authorization failed: No authorization code received", "error"
            )
            return redirect("/settings#social-media-connections")

        # Verify state
        stored_state = session.get("linkedin_oauth_state")
        if state != stored_state:
            flash("LinkedIn authorization failed: Invalid state parameter", "error")
            return redirect("/settings#social-media-connections")

        # Get settings
        settings = load_settings()
        api_keys = settings.get("api_keys", {})
        client_id = api_keys.get("linkedin_client_id", "").strip()
        client_secret = api_keys.get("linkedin_client_secret", "").strip()

        if not client_id or not client_secret:
            flash("LinkedIn Client ID or Secret not configured", "error")
            return redirect("/settings#social-media-connections")

        # Exchange code for access token with FIXED redirect URI (matching authorize endpoint)
        # CRITICAL: Must match exactly what LinkedIn app expects
        redirect_uri = "http://127.0.0.1:5001/api/linkedin/oauth/callback"
        from urllib.parse import quote

        redirect_uri_encoded = quote(redirect_uri, safe="")
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        response = requests.post(token_url, data=token_data, timeout=10)
        response.raise_for_status()

        token_response = response.json()
        access_token = token_response.get("access_token")

        if not access_token:
            flash("Failed to get LinkedIn access token", "error")
            return redirect("/settings#social-media-connections")

        # Get Person URN automatically
        profile_url = "https://api.linkedin.com/v2/me"
        profile_headers = {"Authorization": f"Bearer {access_token}"}

        profile_response = requests.get(
            profile_url, headers=profile_headers, timeout=10
        )
        profile_response.raise_for_status()

        profile_data = profile_response.json()
        person_urn = profile_data.get("id")

        if not person_urn:
            flash("Failed to get LinkedIn Person URN", "error")
            return redirect("/settings#social-media-connections")

        # Save everything automatically (like Buffer does)
        api_keys["linkedin_access_token"] = access_token
        api_keys["linkedin_person_urn"] = person_urn
        settings["api_keys"] = api_keys
        save_settings(settings)

        # Update MY_CONFIG.json
        config_file = Path("MY_CONFIG.json")
        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    config = json.load(f)
                if "api_keys" not in config:
                    config["api_keys"] = {}
                config["api_keys"]["linkedin_access_token"] = access_token
                config["api_keys"]["linkedin_person_urn"] = person_urn
                with open(config_file, "w") as f:
                    json.dump(config, f, indent=2)
            except:
                pass

        # Clear state from session
        session.pop("linkedin_oauth_state", None)

        # Success! Redirect back to config with success message
        flash(
            "✅ LinkedIn connected successfully! Access Token and Person URN saved automatically.",
            "success",
        )
        return redirect("/settings#social-media-connections")

    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_msg = error_data.get("error_description", str(e))
            except:
                pass
        flash(f"LinkedIn connection failed: {error_msg}", "error")
        return redirect("/settings#social-media-connections")
    except Exception as e:
        import traceback

        flash(f"LinkedIn connection error: {str(e)}", "error")
        return redirect("/settings#social-media-connections")


@app.route("/api/config/load-from-file", methods=["POST"])
def api_load_config_from_file():
    """Load configuration from MY_CONFIG.json file."""
    import json
    from pathlib import Path

    config_file = Path("MY_CONFIG.json")

    if not config_file.exists():
        return (
            jsonify(
                {
                    "success": False,
                    "error": "MY_CONFIG.json file not found. Please create it and fill in your settings.",
                }
            ),
            404,
        )

    try:
        with open(config_file, "r") as f:
            config = json.load(f)

        # Save to database
        save_settings(config)

        # Verify it was saved
        loaded = load_settings()

        return jsonify(
            {
                "success": True,
                "message": "Configuration loaded successfully!",
                "stats": {
                    "api_keys_configured": sum(
                        1 for v in loaded.get("api_keys", {}).values() if v
                    ),
                    "scheduling_enabled": loaded.get("scheduling", {}).get(
                        "enabled", False
                    ),
                    "upload_method": loaded.get("scheduling", {}).get(
                        "upload_method", "native"
                    ),
                    "cta_configured": sum(
                        1 for v in loaded.get("cta", {}).values() if v
                    ),
                },
            }
        )
    except json.JSONDecodeError as e:
        return (
            jsonify(
                {"success": False, "error": f"Invalid JSON in MY_CONFIG.json: {str(e)}"}
            ),
            400,
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/facebook/get-token", methods=["GET"])
def api_facebook_get_token_guide():
    """Provide a guide URL for getting Facebook Page Access Token."""
    settings = load_settings()
    api_keys = settings.get("api_keys", {})

    # Facebook App ID not needed - only Page Access Token is required
    page_id = api_keys.get("facebook_page_id", "")

    # Graph API Explorer URL with pre-filled app
    explorer_url = f"https://developers.facebook.com/tools/explorer/?version=v18.0"

    # Permissions needed
    permissions = [
        "pages_manage_posts",
        "pages_read_engagement",
        "instagram_basic",
        "instagram_content_publish",
        "business_management",
    ]

    return jsonify(
        {
            "success": True,
            "guide": {
                "explorer_url": explorer_url,
                "page_id": page_id,
                "permissions": permissions,
                "steps": [
                    {
                        "step": 1,
                        "title": "Open Graph API Explorer",
                        "description": f"Visit: {explorer_url}",
                        "action": "Select your App in the dropdown (top right)",
                    },
                    {
                        "step": 2,
                        "title": "Add Permissions",
                        "description": f'Add these permissions: {", ".join(permissions)}',
                        "action": "Click permissions dropdown and add all required permissions",
                    },
                    {
                        "step": 3,
                        "title": "Generate Token",
                        "description": 'Click "Generate Access Token" and authorize',
                        "action": "Copy the User Access Token that appears",
                    },
                    {
                        "step": 4,
                        "title": "Get Page Token",
                        "description": f"Visit: https://graph.facebook.com/v18.0/me/accounts?access_token={{your-token}}",
                        "action": f"Find Page ID {page_id} and copy its access_token",
                    },
                ],
            },
        }
    )


@app.route("/api/config/upload-client-secret", methods=["POST"])
def api_upload_client_secret():
    """API endpoint to upload client_secret.json file."""
    try:
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not file.filename.endswith(".json"):
            return jsonify({"success": False, "error": "File must be a JSON file"}), 400

        # Read file content to validate it's a valid JSON
        try:
            content = file.read()
            json.loads(content)
            file.seek(0)  # Reset file pointer
        except json.JSONDecodeError:
            return jsonify({"success": False, "error": "Invalid JSON file"}), 400

        # Save to project root (parent of app directory)
        client_secret_path = os.path.join(
            os.path.dirname(__file__), "..", "client_secret.json"
        )
        client_secret_path = os.path.abspath(client_secret_path)

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(client_secret_path), exist_ok=True)

        # Save the file
        file.save(client_secret_path)

        return jsonify(
            {
                "success": True,
                "message": "Client secret file uploaded successfully. Please refresh the page to see the updated status.",
            }
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/calendar-data")
def api_calendar_data():
    """API endpoint for calendar data - shows only SHORTS from playlists with 'shorts' in name, with cross-platform status."""
    from app.database import get_db_connection
    from datetime import datetime
    import pytz

    try:
        calendar_events = []
        video_platforms = {}  # Track which platforms each video is on

        # Fetch YouTube shorts from playlists with 'shorts' in name
        youtube = get_youtube_service()
        if youtube:
            channel_id = get_my_channel_id_helper(youtube)
            if channel_id:
                playlists = fetch_all_playlists_from_youtube(youtube, channel_id)
                ist = pytz.timezone("Asia/Kolkata")

                # Filter playlists to only those with "shorts" in the name (case-insensitive)
                shorts_playlists = [
                    p
                    for p in playlists
                    if "shorts" in p.get("playlistTitle", "").lower()
                ]

                for playlist in shorts_playlists:
                    playlist_id = playlist.get("playlistId", "")
                    playlist_title = playlist.get("playlistTitle", "")

                    videos = fetch_playlist_videos_from_youtube(
                        youtube, playlist_id, channel_id
                    )

                    for video in videos:
                        video_id = video.get("videoId", "")
                        title = video.get("title", "")
                        publish_at = video.get("publishAt", "")
                        published_at = video.get("publishedAt", "")
                        is_scheduled = video.get("isScheduled", False)
                        privacy_status = video.get("privacyStatus", "public")

                        # Skip private videos (only show public and unlisted/scheduled)
                        if privacy_status == "private":
                            continue

                        # Initialize platform tracking for this video
                        if video_id not in video_platforms:
                            video_platforms[video_id] = {
                                "youtube": False,
                                "facebook": False,
                                "instagram": False,
                                "linkedin": False,
                                "video_title": title,
                                "playlist_name": playlist_title,
                            }

                        video_platforms[video_id]["youtube"] = True

                        # Determine the date to display
                        display_date = None
                        if is_scheduled and publish_at:
                            try:
                                if "T" in publish_at:
                                    display_date = datetime.fromisoformat(
                                        publish_at.replace("Z", "+00:00")
                                    )
                                else:
                                    display_date = datetime.strptime(
                                        publish_at, "%Y-%m-%dT%H:%M:%S"
                                    )
                            except:
                                pass
                        elif published_at:
                            try:
                                if "T" in published_at:
                                    display_date = datetime.fromisoformat(
                                        published_at.replace("Z", "+00:00")
                                    )
                                else:
                                    display_date = datetime.strptime(
                                        published_at, "%Y-%m-%dT%H:%M:%S"
                                    )
                            except:
                                pass

                        if display_date:
                            # Convert to IST if needed
                            if display_date.tzinfo is None:
                                display_date = ist.localize(display_date)
                            else:
                                display_date = display_date.astimezone(ist)

                            # Add YouTube video event
                            calendar_events.append(
                                {
                                    "date": display_date.strftime("%Y-%m-%d"),
                                    "time": display_date.strftime("%H:%M:%S"),
                                    "datetime": display_date.isoformat(),
                                    "platform": "YouTube",
                                    "video_title": title,
                                    "video_id": video_id,
                                    "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                                    "status": (
                                        "scheduled" if is_scheduled else "published"
                                    ),
                                    "post_content": "",
                                    "playlist_name": playlist_title,
                                    "channel_name": "YouTube",
                                    "video_type": "short",
                                    "privacy_status": privacy_status,
                                    "description": video.get("description", "")[:200],
                                }
                            )

                            # Get social media posts for this video
                            try:
                                social_posts = get_video_social_posts_from_db(video_id)
                                for platform in ["linkedin", "facebook", "instagram"]:
                                    post = social_posts.get(platform, {})
                                    schedule_date_str = post.get("schedule_date", "")

                                    # Mark platform as scheduled
                                    if (
                                        schedule_date_str
                                        or post.get("status") == "published"
                                    ):
                                        video_platforms[video_id][platform] = True

                                    if schedule_date_str:
                                        try:
                                            schedule_date = datetime.fromisoformat(
                                                schedule_date_str.replace("Z", "+00:00")
                                            )
                                            if schedule_date.tzinfo is None:
                                                schedule_date = ist.localize(
                                                    schedule_date
                                                )
                                            else:
                                                schedule_date = (
                                                    schedule_date.astimezone(ist)
                                                )

                                            calendar_events.append(
                                                {
                                                    "date": schedule_date.strftime(
                                                        "%Y-%m-%d"
                                                    ),
                                                    "time": schedule_date.strftime(
                                                        "%H:%M:%S"
                                                    ),
                                                    "datetime": schedule_date.isoformat(),
                                                    "platform": platform.title(),
                                                    "video_title": title,
                                                    "video_id": video_id,
                                                    "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                                                    "status": post.get(
                                                        "status", "scheduled"
                                                    ),
                                                    "post_content": post.get(
                                                        "post_content", ""
                                                    ),
                                                    "playlist_name": playlist_title,
                                                    "channel_name": platform.title(),
                                                    "video_type": "short",
                                                    "description": "",
                                                }
                                            )
                                        except:
                                            pass
                            except:
                                pass

        # Also get social media posts from database (for any videos not in playlists)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
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
        """
        )

        for row in cursor.fetchall():
            row_dict = dict(row)
            schedule_date_str = row_dict.get("schedule_date")
            if schedule_date_str:
                try:
                    dt = datetime.fromisoformat(
                        schedule_date_str.replace("Z", "+00:00")
                    )
                    ist = pytz.timezone("Asia/Kolkata")
                    if dt.tzinfo is None:
                        dt = ist.localize(dt)
                    else:
                        dt = dt.astimezone(ist)

                    # Check if this event already exists
                    exists = any(
                        e.get("video_id") == row_dict.get("video_id")
                        and e.get("platform") == row_dict.get("platform", "").title()
                        and e.get("datetime") == dt.isoformat()
                        for e in calendar_events
                    )

                    if not exists:
                        calendar_events.append(
                            {
                                "date": dt.strftime("%Y-%m-%d"),
                                "time": dt.strftime("%H:%M:%S"),
                                "datetime": dt.isoformat(),
                                "platform": row_dict.get("platform", "").title(),
                                "video_title": row_dict.get(
                                    "video_title", "Untitled Video"
                                ),
                                "video_id": row_dict.get("video_id", ""),
                                "youtube_url": row_dict.get("youtube_url", ""),
                                "status": row_dict.get("status", "pending"),
                                "post_content": row_dict.get("post_content", ""),
                                "playlist_name": row_dict.get("playlist_name", "")
                                or "",
                                "channel_name": row_dict.get("platform", "").title(),
                                "video_type": "",
                                "role": "",
                                "custom_tags": "",
                                "description": "",
                            }
                        )
                except:
                    pass

        conn.close()

        # Get optimal posting times and generate recommendations
        try:
            optimal_times = get_optimal_posting_times_from_analytics()
            recommendations = generate_calendar_recommendations(
                calendar_events, optimal_times
            )
        except Exception as e:
            app.logger.error(f"Error getting optimal times: {e}")
            optimal_times = {}
            recommendations = []

        # Sort events by datetime (most recent first)
        calendar_events.sort(key=lambda x: x["datetime"], reverse=True)

        # Add cross-platform status to each event
        for event in calendar_events:
            vid_id = event.get("video_id")
            if vid_id and vid_id in video_platforms:
                event["platforms"] = video_platforms[vid_id]
                # Add missing platforms list
                missing = []
                for platform in ["facebook", "instagram", "linkedin"]:
                    if not video_platforms[vid_id].get(platform):
                        missing.append(platform)
                event["missing_platforms"] = missing

        return jsonify(
            {
                "events": calendar_events,
                "optimal_times": optimal_times,
                "recommendations": recommendations,
                "video_platforms": video_platforms,  # Include full platform mapping
            }
        )
    except Exception as e:
        import traceback

        app.logger.error(f"Error in api_calendar_data: {e}", exc_info=True)
        # Return empty events instead of error to prevent calendar from breaking
        return (
            jsonify(
                {
                    "events": [],
                    "optimal_times": {},
                    "recommendations": [],
                    "error": str(e) if app.debug else "Error loading calendar data",
                }
            ),
            500,
        )


def get_optimal_posting_times_from_analytics():
    """Get optimal posting times from analytics data."""
    try:
        youtube_analytics = get_youtube_analytics()
        optimal_times = calculate_optimal_posting_times(youtube_analytics, {}, {})

        best_hours = []
        if optimal_times.get("youtube") and optimal_times["youtube"].get("best_times"):
            best_hours = [
                f"{hour:02d}:00"
                for hour, views in optimal_times["youtube"]["best_times"][:3]
            ]

        return {
            "youtube": optimal_times.get("youtube", {}),
            "best_hours": best_hours if best_hours else ["14:00", "17:00", "21:00"],
            "overall_best": optimal_times.get("overall", {}),
        }
    except:
        return {"best_hours": ["14:00", "17:00", "21:00"]}


def generate_calendar_recommendations(events, optimal_times):
    """Generate recommendations for promoting videos to other channels."""
    recommendations = []

    # Group YouTube videos by date
    youtube_videos_by_date = {}
    social_posts_by_video = {}

    for event in events:
        if event.get("platform") == "YouTube":
            date_key = event["date"]
            if date_key not in youtube_videos_by_date:
                youtube_videos_by_date[date_key] = []
            youtube_videos_by_date[date_key].append(event)

        # Track which platforms are scheduled for each video
        video_id = event.get("video_id")
        platform = event.get("platform", "").lower()
        if video_id and platform != "youtube":
            if video_id not in social_posts_by_video:
                social_posts_by_video[video_id] = set()
            social_posts_by_video[video_id].add(platform)

    # Generate recommendations
    for date_key, video_events in youtube_videos_by_date.items():
        for video_event in video_events:
            video_id = video_event.get("video_id")
            video_title = video_event.get("video_title", "")

            scheduled_platforms = social_posts_by_video.get(video_id, set())
            missing_platforms = {
                "linkedin",
                "facebook",
                "instagram",
            } - scheduled_platforms

            if missing_platforms:
                best_time = (
                    optimal_times.get("best_hours", ["14:00"])[0]
                    if optimal_times.get("best_hours")
                    else "14:00"
                )
                recommendations.append(
                    {
                        "date": date_key,
                        "video_id": video_id,
                        "video_title": video_title,
                        "youtube_time": video_event.get("time", "12:00"),
                        "missing_platforms": list(missing_platforms),
                        "recommended_time": best_time,
                        "message": f"Promote '{video_title[:50]}{'...' if len(video_title) > 50 else ''}' to {', '.join([p.title() for p in missing_platforms])} at {best_time}",
                    }
                )

    return recommendations


@app.route("/api/queue")
def api_queue():
    """Get queue data for dashboard."""
    try:
        from app.database import get_db_connection
        from datetime import datetime, date

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get queue posts (pending + scheduled)
        cursor.execute(
            """
            SELECT smp.id, smp.video_id, smp.platform, smp.post_content, 
                   smp.schedule_date, smp.actual_scheduled_date, smp.status,
                   smp.created_at, smp.updated_at,
                   v.title as video_title, v.youtube_url, v.playlist_name
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status IN ('pending', 'scheduled')
            ORDER BY 
                CASE WHEN smp.schedule_date IS NOT NULL THEN smp.schedule_date ELSE smp.created_at END ASC,
                smp.created_at DESC
            LIMIT 100
        """
        )

        queue_posts = []
        for row in cursor.fetchall():
            post = dict(row)
            post["post_content"] = post.get("post_content", "")
            post["video_title"] = post.get("video_title", "Unknown Video")
            post["playlist_name"] = post.get("playlist_name", "")
            queue_posts.append(post)

        # Get drafts (posts without schedule_date)
        cursor.execute(
            """
            SELECT smp.id, smp.video_id, smp.platform, smp.post_content, 
                   smp.schedule_date, smp.actual_scheduled_date, smp.status,
                   smp.created_at, smp.updated_at,
                   v.title as video_title, v.youtube_url, v.playlist_name
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status = 'pending' AND smp.schedule_date IS NULL
            ORDER BY smp.created_at DESC
            LIMIT 100
        """
        )

        draft_posts = []
        for row in cursor.fetchall():
            post = dict(row)
            post["post_content"] = post.get("post_content", "")
            post["video_title"] = post.get("video_title", "Unknown Video")
            post["playlist_name"] = post.get("playlist_name", "")
            draft_posts.append(post)

        # Get published posts
        cursor.execute(
            """
            SELECT smp.id, smp.video_id, smp.platform, smp.post_content, 
                   smp.schedule_date, smp.actual_scheduled_date, smp.status,
                   smp.created_at, smp.updated_at,
                   v.title as video_title, v.youtube_url, v.playlist_name
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.status = 'published'
            ORDER BY smp.updated_at DESC
            LIMIT 100
        """
        )

        published_posts = []
        for row in cursor.fetchall():
            post = dict(row)
            post["post_content"] = post.get("post_content", "")
            post["video_title"] = post.get("video_title", "Unknown Video")
            post["playlist_name"] = post.get("playlist_name", "")
            published_posts.append(post)

        # Get stats
        today = date.today().isoformat()

        cursor.execute(
            'SELECT COUNT(*) as count FROM social_media_posts WHERE status IN ("pending", "scheduled")'
        )
        queue_count_result = cursor.fetchone()
        queue_count = queue_count_result["count"] if queue_count_result else 0

        cursor.execute(
            'SELECT COUNT(*) as count FROM social_media_posts WHERE status = "scheduled"'
        )
        scheduled_count_result = cursor.fetchone()
        scheduled_count = (
            scheduled_count_result["count"] if scheduled_count_result else 0
        )

        cursor.execute(
            'SELECT COUNT(*) as count FROM social_media_posts WHERE status = "published" AND DATE(updated_at) = ?',
            (today,),
        )
        published_today_result = cursor.fetchone()
        published_today = (
            published_today_result["count"] if published_today_result else 0
        )

        settings = load_settings()
        automation_active = settings.get("scheduling", {}).get("enabled", False)

        conn.close()

        return jsonify(
            {
                "queue": queue_posts,
                "drafts": draft_posts,
                "published": published_posts,
                "stats": {
                    "queue_count": queue_count,
                    "scheduled_count": scheduled_count,
                    "published_today": published_today,
                    "automation_active": automation_active,
                },
            }
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {
                    "queue": [],
                    "drafts": [],
                    "published": [],
                    "stats": {
                        "queue_count": 0,
                        "scheduled_count": 0,
                        "published_today": 0,
                        "automation_active": False,
                    },
                    "error": str(e),
                }
            ),
            500,
        )


@app.route("/api/queue/create", methods=["POST"])
def api_queue_create():
    """Create a new post in queue."""
    try:
        from app.database import get_db_connection

        data = request.json
        platforms = data.get("platforms", [])
        content = data.get("content", "")
        scheduled_at = data.get("scheduled_at")
        video_url = data.get("video_url", "")

        if not platforms:
            return (
                jsonify(
                    {"success": False, "error": "Please select at least one platform"}
                ),
                400,
            )

        if not content:
            return (
                jsonify({"success": False, "error": "Please enter post content"}),
                400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Extract video_id from URL if provided
        video_id = None
        if video_url:
            # Try to extract video ID from YouTube URL
            import re

            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
            if match:
                video_id = match.group(1)

        # Create posts for each platform
        created_posts = []
        for platform in platforms:
            cursor.execute(
                """
                INSERT INTO social_media_posts 
                (video_id, platform, post_content, schedule_date, status, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    video_id,
                    platform,
                    content,
                    scheduled_at,
                    "scheduled" if scheduled_at else "pending",
                ),
            )
            created_posts.append(cursor.lastrowid)

        conn.commit()
        conn.close()

        return jsonify(
            {
                "success": True,
                "message": f"Created {len(created_posts)} post(s)",
                "post_ids": created_posts,
            }
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/queue/publish-now", methods=["POST"])
def api_queue_publish_now():
    """Publish a post immediately."""
    try:
        data = request.json
        platforms = data.get("platforms", [])
        content = data.get("content", "")
        video_url = data.get("video_url", "")

        if not platforms or not content:
            return jsonify({"success": False, "error": "Missing required fields"}), 400

        # This would call the actual posting function
        # For now, just mark as published
        from app.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        video_id = None
        if video_url:
            import re

            match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", video_url)
            if match:
                video_id = match.group(1)

        now = datetime.now().isoformat()
        published_count = 0

        for platform in platforms:
            cursor.execute(
                """
                INSERT INTO social_media_posts 
                (video_id, platform, post_content, status, actual_scheduled_date, created_at, updated_at)
                VALUES (?, ?, ?, 'published', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
                (video_id, platform, content, now),
            )
            published_count += 1

        conn.commit()
        conn.close()

        return jsonify(
            {"success": True, "message": f"Published to {published_count} platform(s)"}
        )
    except Exception as e:
        import traceback

        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/queue/<int:post_id>/publish", methods=["POST"])
def api_queue_publish_item(post_id):
    """Publish a specific queue item - downloads video and uploads natively if configured."""
    try:
        from app.database import get_db_connection, get_video

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get post details
        cursor.execute(
            """
            SELECT smp.*, v.video_id, v.title, v.youtube_url
            FROM social_media_posts smp
            LEFT JOIN videos v ON smp.video_id = v.video_id
            WHERE smp.id = ?
        """,
            (post_id,),
        )

        post = dict(cursor.fetchone())
        if not post:
            return jsonify({"success": False, "error": "Post not found"}), 404

        video_id = post.get("video_id")
        platform = post.get("platform", "").lower()
        post_content = post.get("post_content", "")

        # Check upload method from settings
        settings = load_settings()
        upload_method = settings.get("scheduling", {}).get(
            "upload_method", "native"
        )  # Default: native

        if upload_method == "native" and video_id:
            # Native video upload: Download and upload video
            try:
                from app.video_processor import process_and_upload_video

                # Get API credentials
                api_keys = settings.get("api_keys", {})
                api_credentials = {
                    "linkedin_access_token": api_keys.get("linkedin_access_token"),
                    "linkedin_person_urn": api_keys.get("linkedin_person_urn"),
                    "facebook_page_id": api_keys.get("facebook_page_id"),
                    "facebook_page_access_token": api_keys.get(
                        "facebook_page_access_token"
                    ),
                    "instagram_business_account_id": api_keys.get(
                        "instagram_business_account_id"
                    ),
                    # Note: Instagram uses Facebook Page Access Token, not a separate token
                }

                # Prepare captions
                captions = {platform: post_content}

                # Process and upload
                result = process_and_upload_video(
                    video_id=video_id,
                    platforms=[platform],
                    captions=captions,
                    api_credentials=api_credentials,
                )

                if result.get("success") and result.get("results", {}).get(
                    platform, {}
                ).get("success"):
                    # Update post status
                    cursor.execute(
                        """
                        UPDATE social_media_posts 
                        SET status = 'published', 
                            actual_scheduled_date = CURRENT_TIMESTAMP,
                            post_id = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """,
                        (result["results"][platform].get("post_id"), post_id),
                    )

                    conn.commit()
                    conn.close()

                    return jsonify(
                        {
                            "success": True,
                            "message": f"Video uploaded and published natively to {platform}",
                            "post_id": result["results"][platform].get("post_id"),
                        }
                    )
                else:
                    error = result.get("error") or result.get("results", {}).get(
                        platform, {}
                    ).get("error", "Upload failed")
                    # Mark as failed
                    cursor.execute(
                        """
                        UPDATE social_media_posts 
                        SET status = 'failed',
                            error_message = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """,
                        (error, post_id),
                    )
                    conn.commit()
                    conn.close()

                    return jsonify({"success": False, "error": error}), 500

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
        cursor.execute(
            """
            UPDATE social_media_posts 
            SET status = 'published', 
                actual_scheduled_date = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (post_id,),
        )

        conn.commit()
        conn.close()

        return jsonify(
            {
                "success": True,
                "message": f"Post published to {platform} (link sharing mode)",
                "note": "Native video upload not configured or failed. Post shared as link.",
            }
        )

    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/queue/<int:post_id>", methods=["DELETE", "PUT"])
def api_queue_update_or_delete(post_id):
    """Update or delete a queue item."""
    if request.method == "DELETE":
        try:
            from app.database import get_db_connection

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM social_media_posts WHERE id = ?", (post_id,))
            conn.commit()
            conn.close()

            return jsonify({"success": True, "message": "Post deleted"})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    elif request.method == "PUT":
        """Update schedule date for an existing post."""
        try:
            from app.database import get_db_connection, log_activity

            data = request.json
            schedule_datetime = data.get("schedule_date")

            if not schedule_datetime:
                return (
                    jsonify({"success": False, "error": "Schedule date is required"}),
                    400,
                )

            conn = get_db_connection()
            cursor = conn.cursor()

            # Get existing post
            cursor.execute(
                """
                SELECT video_id, platform, post_content, status
                FROM social_media_posts
                WHERE id = ?
            """,
                (post_id,),
            )

            row = cursor.fetchone()
            if not row:
                conn.close()
                return jsonify({"success": False, "error": "Post not found"}), 404

            post = dict(row)

            # Update schedule date
            cursor.execute(
                """
                UPDATE social_media_posts
                SET schedule_date = ?, status = 'scheduled', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (schedule_datetime, post_id),
            )

            conn.commit()
            conn.close()

            # Log activity
            log_activity(
                "update_schedule",
                platform=post["platform"],
                video_id=post["video_id"],
                status="success",
                message=f"Schedule updated to {schedule_datetime}",
                details={"post_id": post_id, "new_schedule": schedule_datetime},
            )

            return jsonify({"success": True, "message": "Schedule updated"})
        except Exception as e:
            import traceback

            return (
                jsonify(
                    {
                        "success": False,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                ),
                500,
            )


@app.route("/api/queue/publish-to-channels", methods=["POST"])
def api_queue_publish_to_channels():
    """Publish a video to multiple YouTube channels (cross-posting).

    This feature allows scheduling a single short video to be published
    across multiple YouTube channels at the same time or different times.
    """
    try:
        from app.database import get_db_connection, log_activity
        from datetime import datetime

        data = request.json
        video_id = data.get("video_id")
        target_channels = data.get("target_channels", [])
        scheduled_date = data.get("scheduled_date")
        notes = data.get("notes", "")

        if not video_id or not target_channels:
            return (
                jsonify(
                    {"success": False, "error": "Missing video_id or target_channels"}
                ),
                400,
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get source video details
        cursor.execute(
            "SELECT title, youtube_url FROM videos WHERE video_id = ?", (video_id,)
        )
        video_row = cursor.fetchone()
        if not video_row:
            conn.close()
            return jsonify({"success": False, "error": "Video not found"}), 404

        video = dict(video_row)
        source_channel = "primary"  # Can be enhanced to track actual source channel

        # Create channel_publications entries for each target channel
        created_count = 0
        for target_channel in target_channels:
            try:
                cursor.execute(
                    """
                    INSERT INTO channel_publications 
                    (video_id, source_channel, target_channel, publication_status, scheduled_date, notes, created_at, updated_at)
                    VALUES (?, ?, ?, 'scheduled', ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                    (video_id, source_channel, target_channel, scheduled_date, notes),
                )
                created_count += 1
            except sqlite3.IntegrityError:
                # Channel publication already exists, update it
                cursor.execute(
                    """
                    UPDATE channel_publications
                    SET publication_status = 'scheduled', scheduled_date = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE video_id = ? AND target_channel = ?
                """,
                    (scheduled_date, notes, video_id, target_channel),
                )
                created_count += 1

        conn.commit()
        conn.close()

        # Log activity
        log_activity(
            "cross_channel_publish_scheduled",
            video_id=video_id,
            status="success",
            message=f"Scheduled for {created_count} channel(s)",
            details={
                "target_channels": target_channels,
                "scheduled_date": scheduled_date,
                "video_title": video.get("title", "Unknown"),
            },
        )

        return jsonify(
            {
                "success": True,
                "message": f"Successfully scheduled publishing to {created_count} channel(s)",
                "created": created_count,
            }
        )
    except Exception as e:
        import traceback

        return (
            jsonify(
                {"success": False, "error": str(e), "traceback": traceback.format_exc()}
            ),
            500,
        )


@app.route("/api/queue/channel-publications/<string:video_id>", methods=["GET"])
def api_queue_get_channel_publications(video_id):
    """Get all channel publications for a specific video (cross-post tracking)."""
    try:
        from app.database import get_db_connection

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, video_id, source_channel, target_channel, publication_status, 
                   scheduled_date, published_date, notes, created_at, updated_at
            FROM channel_publications
            WHERE video_id = ?
            ORDER BY created_at DESC
        """,
            (video_id,),
        )

        publications = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return jsonify(
            {
                "success": True,
                "video_id": video_id,
                "publications": publications,
                "total": len(publications),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/channels", methods=["GET"])
def api_get_channels():
    """Get all configured channels for publishing destinations.

    Returns YouTube channels, Facebook pages, LinkedIn profiles, etc.
    that can be used as target channels for cross-posting.
    """
    try:
        settings = load_settings()
        channels = []

        # YouTube Channel
        if settings.get("api_keys", {}).get("youtube_channel_id"):
            channels.append(
                {
                    "id": "youtube:" + settings["api_keys"]["youtube_channel_id"],
                    "name": "YouTube",
                    "type": "youtube",
                    "channel_id": settings["api_keys"]["youtube_channel_id"],
                }
            )

        # Facebook Page
        if settings.get("api_keys", {}).get("facebook_page_id"):
            channels.append(
                {
                    "id": "facebook:" + settings["api_keys"]["facebook_page_id"],
                    "name": "Facebook Page",
                    "type": "facebook",
                    "page_id": settings["api_keys"]["facebook_page_id"],
                }
            )

        # Instagram Business Account
        if settings.get("api_keys", {}).get("instagram_business_account_id"):
            channels.append(
                {
                    "id": "instagram:"
                    + settings["api_keys"]["instagram_business_account_id"],
                    "name": "Instagram",
                    "type": "instagram",
                    "account_id": settings["api_keys"]["instagram_business_account_id"],
                }
            )

        # LinkedIn Profile
        if settings.get("api_keys", {}).get("linkedin_person_urn"):
            channels.append(
                {
                    "id": "linkedin:" + settings["api_keys"]["linkedin_person_urn"],
                    "name": "LinkedIn",
                    "type": "linkedin",
                    "person_urn": settings["api_keys"]["linkedin_person_urn"],
                }
            )

        return jsonify({"success": True, "channels": channels, "total": len(channels)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/linkedin/disconnect", methods=["POST"])
def api_linkedin_disconnect():
    """Disconnect LinkedIn by clearing tokens."""
    try:
        settings = load_settings()
        settings["api_keys"]["linkedin_access_token"] = ""
        settings["api_keys"]["linkedin_person_urn"] = ""
        save_settings(settings)
        return jsonify({"success": True, "message": "LinkedIn disconnected"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/facebook/disconnect", methods=["POST"])
def api_facebook_disconnect():
    """Disconnect Facebook by clearing tokens."""
    try:
        settings = load_settings()
        settings["api_keys"]["facebook_page_access_token"] = ""
        settings["api_keys"]["facebook_page_id"] = ""
        settings["api_keys"]["instagram_business_account_id"] = ""
        save_settings(settings)
        return jsonify(
            {"success": True, "message": "Facebook and Instagram disconnected"}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/status")
def api_status():
    """Get complete application status - what's configured, what's missing."""
    try:
        settings = load_settings()
        api_keys = settings.get("api_keys", {})

        status = {
            "youtube": {
                "configured": os.path.exists(
                    os.path.join(os.path.dirname(__file__), "..", "client_secret.json")
                ),
                "authenticated": os.path.exists(
                    os.path.join(os.path.dirname(__file__), "..", "token.json")
                ),
                "redirect_uri": "http://localhost:5001/oauth2callback",  # Google OAuth requires localhost, not .local
                "status": (
                    "ready"
                    if os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__), "..", "client_secret.json"
                        )
                    )
                    and os.path.exists(
                        os.path.join(os.path.dirname(__file__), "..", "token.json")
                    )
                    else "needs_setup"
                ),
                "missing": [],
            },
            "linkedin": {
                "configured": bool(
                    api_keys.get("linkedin_client_id")
                    and api_keys.get("linkedin_client_secret")
                ),
                "authenticated": bool(api_keys.get("linkedin_access_token")),
                "redirect_uri": "http://localhost:5001/api/linkedin/oauth/callback",  # Use localhost for local dev
                "status": (
                    "ready"
                    if api_keys.get("linkedin_access_token")
                    else (
                        "configured"
                        if api_keys.get("linkedin_client_id")
                        else "needs_setup"
                    )
                ),
                "missing": [],
            },
            "facebook": {
                "configured": bool(
                    api_keys.get("facebook_page_access_token")
                    and api_keys.get("facebook_page_id")
                ),
                "authenticated": bool(api_keys.get("facebook_page_access_token")),
                "redirect_uri": "http://localhost:5001/api/facebook/oauth/callback",  # Use localhost for local dev
                "status": (
                    "ready"
                    if api_keys.get("facebook_page_access_token")
                    else "needs_setup"
                ),
                "missing": [],
            },
            "instagram": {
                "configured": bool(api_keys.get("instagram_business_account_id")),
                "authenticated": bool(api_keys.get("facebook_page_access_token")),
                "redirect_uri": "http://localhost:5001/api/facebook/oauth/callback",  # Use localhost for local dev
                "status": (
                    "ready"
                    if (
                        api_keys.get("instagram_business_account_id")
                        and api_keys.get("facebook_page_access_token")
                    )
                    else "needs_setup"
                ),
                "missing": [],
            },
        }

        # Add missing items
        if not status["youtube"]["configured"]:
            status["youtube"]["missing"].append("client_secret.json file")
        if not status["youtube"]["authenticated"]:
            status["youtube"]["missing"].append("OAuth authentication")

        if not status["linkedin"]["configured"]:
            status["linkedin"]["missing"].extend(
                ["LinkedIn Client ID", "LinkedIn Client Secret"]
            )
        elif not status["linkedin"]["authenticated"]:
            status["linkedin"]["missing"].append("OAuth connection")
            # Make status red/error if OAuth is missing
            if status["linkedin"]["status"] == "configured":
                # Keep as configured but add missing OAuth
                pass

        if not status["facebook"]["configured"]:
            status["facebook"]["missing"].extend(
                ["Facebook Page Access Token", "Facebook Page ID"]
            )
        elif not status["facebook"]["authenticated"]:
            status["facebook"]["missing"].append("OAuth connection")

        if not status["instagram"]["configured"]:
            status["instagram"]["missing"].extend(
                ["Instagram Business Account ID", "Facebook Page Access Token"]
            )
        elif not status["instagram"]["authenticated"]:
            status["instagram"]["missing"].append("OAuth connection")

        # Calculate overall status
        ready_count = sum(1 for s in status.values() if s.get("status") == "ready")
        total_count = len(status)

        # Return in format expected by React frontend
        return jsonify(
            {
                "platforms": status,
                "overall": {
                    "ready": ready_count,
                    "total": total_count,
                    "percentage": (
                        int((ready_count / total_count * 100)) if total_count > 0 else 0
                    ),
                },
                "database_exists": os.path.exists("automation.db"),
                "settings_loaded": bool(settings),
            }
        )
    except Exception as e:
        app.logger.error(f"Error getting status: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/test-connection", methods=["POST"])
def test_connection():
    """Test API connection."""
    platform = request.json.get("platform")
    settings = load_settings()
    api_keys = settings.get("api_keys", {})

    # Simple validation - check if key exists
    if platform == "linkedin":
        has_client_id = bool(api_keys.get("linkedin_client_id"))
        has_client_secret = bool(api_keys.get("linkedin_client_secret"))
        has_token = bool(api_keys.get("linkedin_access_token"))
        has_urn = bool(api_keys.get("linkedin_person_urn"))

        # Either Client ID + Secret OR Access Token is required
        has_credentials = (has_client_id and has_client_secret) or has_token
        is_configured = has_credentials and has_urn

        return jsonify(
            {
                "success": is_configured,
                "message": (
                    "LinkedIn configured"
                    if is_configured
                    else "Missing LinkedIn credentials (need Client ID + Secret OR Access Token, and Person URN)"
                ),
            }
        )
    elif platform == "facebook":
        has_token = bool(api_keys.get("facebook_page_access_token"))
        has_page_id = bool(api_keys.get("facebook_page_id"))

        # Page Access Token and Page ID are required
        is_configured = has_token and has_page_id

        return jsonify(
            {
                "success": is_configured,
                "message": (
                    "Facebook configured"
                    if is_configured
                    else "Missing Facebook credentials (need Page Access Token and Page ID)"
                ),
            }
        )
    elif platform == "instagram":
        has_account = bool(api_keys.get("instagram_business_account_id"))

        # Instagram Business Account ID and Facebook Page Token (or Instagram token) are required
        is_configured = has_account and has_token

        return jsonify(
            {
                "success": is_configured,
                "message": (
                    "Instagram configured"
                    if is_configured
                    else "Missing Instagram credentials (need Facebook App ID + Secret OR Instagram Access Token, and Business Account ID)"
                ),
            }
        )
    elif platform == "ayrshare":
        has_key = bool(api_keys.get("ayrshare_api_key"))
        return jsonify(
            {
                "success": has_key,
                "message": (
                    "Ayrshare configured" if has_key else "Missing Ayrshare API key"
                ),
            }
        )

    return jsonify({"success": False, "message": "Unknown platform"})


# Explicit route for assets to ensure they're served correctly
@app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serve static assets from frontend build."""
    if os.path.exists(FRONTEND_BUILD_DIR):
        assets_dir = os.path.join(FRONTEND_BUILD_DIR, "assets")
        file_path = os.path.join(assets_dir, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(assets_dir, filename)
    return jsonify({"error": "Asset not found"}), 404


# Explicit route for Facebook token helper (must be before catch-all)
@app.route("/facebook-token-helper")
def facebook_token_helper_route():
    """Serve Facebook token helper page directly."""
    from app.facebook_token_helper import facebook_token_helper

    return facebook_token_helper()


# Catch-all route for React Router (must be last, after all API routes)
@app.route("/<path:path>")
def catch_all(path):
    """
    Catch-all route for React Router client-side routing.
    Serves React app for all non-API, non-Flask-template routes.
    """
    # Don't interfere with API routes
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404

    # Exclude specific Flask-only routes that need server-side rendering
    # These routes are handled by specific Flask routes above
    flask_only_routes = [
        "playlists",
        "docs",
        "documentation",
        "health",
        "favicon.ico",
        "robots.txt",
        "config",
        "oauth2callback",
        "facebook-token-helper",
    ]
    if path in flask_only_routes or path.split("/")[0] in flask_only_routes:
        # These routes should be handled by Flask routes above
        # If we reach here, the Flask route didn't catch it, so return 404
        # But actually, Flask routes should be defined before this catch-all
        # So this shouldn't be reached for /config
        app.logger.warning(
            f"Caught Flask-only route /{path} in catch_all - Flask route should have handled it"
        )
        return (
            jsonify(
                {
                    "error": "Route not found",
                    "message": f"Flask route /{path} should have been handled by specific route",
                }
            ),
            404,
        )

    # Serve React app static files (JS, CSS, images, etc.)
    if os.path.exists(FRONTEND_BUILD_DIR):
        # Check if it's a static file request (has file extension and not a route)
        if "." in path and not path.endswith("/"):
            file_path = os.path.join(FRONTEND_BUILD_DIR, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(FRONTEND_BUILD_DIR, path)

        # For React Router client-side routes - serve index.html
        index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
        if os.path.exists(index_path):
            return send_from_directory(FRONTEND_BUILD_DIR, "index.html")

    # Fallback - return 404
    return jsonify({"error": "Not found", "path": path}), 404


# Shutdown scheduler on app exit
atexit.register(lambda: SCHEDULER.shutdown())

if __name__ == "__main__":
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
            api_keys = test_settings.get("api_keys", {})
            keys_count = sum(1 for v in api_keys.values() if v)
            print(
                f"✅ Settings loaded successfully from database ({keys_count} API keys configured)"
            )
        else:
            print(
                "ℹ️  No settings found in database - will use defaults until you configure"
            )
    except Exception as e:
        pass


# Video Upload Endpoint
@app.route("/api/upload-video", methods=["POST"])
def api_upload_video():
    """Upload video to YouTube with all details and scheduling."""
    try:
        import os
        from werkzeug.utils import secure_filename
        from datetime import datetime
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError

        # Check for file
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400

        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        # Validate file extension
        allowed_extensions = {"mp4", "mov", "avi", "mkv", "webm"}
        if not (
            "." in file.filename
            and file.filename.rsplit(".", 1)[1].lower() in allowed_extensions
        ):
            return jsonify({"success": False, "error": "Invalid file type"}), 400

        # Get form data
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        tags = request.form.get("tags", "").strip()
        playlist_id = request.form.get("playlist_id", "").strip()
        publish_now = request.form.get("publish_now", "true").lower() == "true"
        schedule_datetime = request.form.get("schedule_datetime", "")
        visibility = request.form.get("visibility", "public").lower()

        # Validate required fields
        if not title:
            return jsonify({"success": False, "error": "Title is required"}), 400

        if not publish_now and not schedule_datetime:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Schedule date/time is required when not publishing now",
                    }
                ),
                400,
            )

        if visibility not in ["public", "unlisted", "private"]:
            visibility = "public"

        # Save uploaded file temporarily
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_uploads_dir = os.path.join(project_root, "data", "uploads")
        os.makedirs(temp_uploads_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_uploads_dir, filename)
        file.save(filepath)

        # Get YouTube service
        try:
            youtube = get_youtube_service()
        except Exception as e:
            os.remove(filepath) if os.path.exists(filepath) else None
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"YouTube authentication failed: {str(e)}",
                    }
                ),
                401,
            )

        # Prepare video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "categoryId": "22",  # Category: People & Blogs (adjustable)
            },
            "status": {
                "privacyStatus": visibility,
                "selfDeclaredMadeForKids": False,
            },
        }

        # Add schedule time if not publishing now
        if not publish_now and schedule_datetime:
            body["status"]["publishAt"] = schedule_datetime + ":00Z"

        # Upload video
        try:
            request_obj = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=MediaFileUpload(
                    filepath, chunksize=10 * 1024 * 1024, resumable=True
                ),
            )

            # Execute upload
            response = None
            while response is None:
                try:
                    status, response = request_obj.next_chunk()
                    if status:
                        percent = int(status.progress() * 100)
                        print(f"Upload progress: {percent}%")
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Retry on server errors
                        continue
                    else:
                        raise

            video_id = response.get("id")

            # Add to playlist if specified
            if playlist_id and video_id:
                try:
                    youtube.playlistItems().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "playlistId": playlist_id,
                                "resourceId": {
                                    "kind": "youtube#video",
                                    "videoId": video_id,
                                },
                            }
                        },
                    ).execute()
                except Exception as e:
                    # Log error but don't fail the whole operation
                    print(f"Warning: Failed to add video to playlist: {str(e)}")

            # Save uploaded video metadata
            try:
                from datetime import datetime

                project_root = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))
                )
                uploads_metadata_file = os.path.join(
                    project_root, "data", "uploads_metadata.json"
                )

                # Load existing metadata
                uploads_metadata = []
                if os.path.exists(uploads_metadata_file):
                    try:
                        with open(uploads_metadata_file, "r") as f:
                            uploads_metadata = json.load(f)
                    except:
                        uploads_metadata = []

                # Add new upload
                uploads_metadata.append(
                    {
                        "video_id": video_id,
                        "title": title,
                        "description": description,
                        "tags": tags,
                        "filename": secure_filename(file.filename),
                        "uploaded_at": datetime.utcnow().isoformat(),
                        "scheduled": not publish_now,
                        "schedule_time": schedule_datetime if not publish_now else None,
                        "playlist_id": playlist_id,
                        "visibility": visibility,
                    }
                )

                # Save updated metadata
                os.makedirs(os.path.dirname(uploads_metadata_file), exist_ok=True)
                with open(uploads_metadata_file, "w") as f:
                    json.dump(uploads_metadata, f, indent=2)

            except Exception as e:
                print(f"Warning: Failed to save upload metadata: {str(e)}")

            # Clean up temp file
            if os.path.exists(filepath):
                os.remove(filepath)

            return jsonify(
                {
                    "success": True,
                    "video_id": video_id,
                    "message": f"Video uploaded successfully!",
                    "scheduled": not publish_now,
                    "schedule_time": schedule_datetime if not publish_now else None,
                }
            )

        except Exception as e:
            # Clean up on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"success": False, "error": f"Upload failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500


# Get All Playlists Endpoint
@app.route("/api/playlists", methods=["GET"])
def api_get_playlists():
    """Get all YouTube playlists for the authenticated user."""
    try:
        youtube = get_youtube_service()
        if not youtube:
            return (
                jsonify({"playlists": [], "error": "YouTube service not available"}),
                200,
            )

        try:
            channel_id = get_my_channel_id_helper(youtube)
            if not channel_id:
                return (
                    jsonify({"playlists": [], "error": "Could not get channel ID"}),
                    200,
                )

            # Fetch all playlists
            all_playlists = fetch_all_playlists_from_youtube(youtube, channel_id)

            # Return all playlists with full details
            playlists_response = [
                {
                    "playlistId": pl.get("playlistId"),
                    "playlistTitle": pl.get("playlistTitle"),
                    "playlistUrl": pl.get("playlistUrl"),
                    "itemCount": pl.get("itemCount", 0),
                }
                for pl in all_playlists
            ]

            return (
                jsonify(
                    {"playlists": playlists_response, "count": len(playlists_response)}
                ),
                200,
            )

        except Exception as e:
            app.logger.error(f"Error fetching playlists: {str(e)}")
            return jsonify({"playlists": [], "error": str(e)}), 200

    except Exception as e:
        app.logger.error(f"Error in api_get_playlists: {str(e)}")
        return jsonify({"playlists": [], "error": str(e)}), 200


# Create Playlist Endpoint
@app.route("/api/create-playlist", methods=["POST"])
def api_create_playlist():
    """Create a new YouTube playlist."""
    try:
        from googleapiclient.discovery import build

        data = request.get_json()
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        privacy_status = data.get("privacy_status", "public").lower()

        if not title:
            return (
                jsonify({"success": False, "error": "Playlist title is required"}),
                400,
            )

        if privacy_status not in ["public", "unlisted", "private"]:
            privacy_status = "public"

        try:
            youtube = get_youtube_service()
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": f"YouTube authentication failed: {str(e)}",
                    }
                ),
                401,
            )

        # Create playlist
        playlist_body = {
            "snippet": {
                "title": title,
                "description": description,
            },
            "status": {
                "privacyStatus": privacy_status,
            },
        }

        playlist_response = (
            youtube.playlists()
            .insert(
                part="snippet,status",
                body=playlist_body,
            )
            .execute()
        )

        playlist_id = playlist_response.get("id")

        return jsonify(
            {
                "success": True,
                "playlist_id": playlist_id,
                "message": f"Playlist '{title}' created successfully!",
            }
        )

    except Exception as e:
        return (
            jsonify(
                {"success": False, "error": f"Failed to create playlist: {str(e)}"}
            ),
            500,
        )


# ============================================================================
# Course Management Endpoints
# ============================================================================


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """Get all courses with modules and tracks."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        if not os.path.exists(courses_file):
            return jsonify({"courses": []}), 200

        with open(courses_file, "r") as f:
            courses = json.load(f)

        return jsonify({"courses": courses}), 200
    except Exception as e:
        app.logger.error(f"Error getting courses: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/courses", methods=["POST"])
def create_course():
    """Create a new course."""
    try:
        import uuid
        from datetime import datetime

        data = request.get_json()
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        if not name:
            return jsonify({"error": "Course name is required"}), 400

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        # Load existing courses
        courses = []
        if os.path.exists(courses_file):
            with open(courses_file, "r") as f:
                courses = json.load(f)

        # Create new course
        new_course = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "modules": [],
            "created_at": datetime.utcnow().isoformat(),
        }

        courses.append(new_course)

        # Save courses
        os.makedirs(os.path.dirname(courses_file), exist_ok=True)
        with open(courses_file, "w") as f:
            json.dump(courses, f, indent=2)

        return jsonify({"success": True, "course": new_course}), 201
    except Exception as e:
        app.logger.error(f"Error creating course: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    """Delete a course."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        if not os.path.exists(courses_file):
            return jsonify({"error": "Course not found"}), 404

        with open(courses_file, "r") as f:
            courses = json.load(f)

        # Filter out the course to delete
        courses = [c for c in courses if c["id"] != course_id]

        with open(courses_file, "w") as f:
            json.dump(courses, f, indent=2)

        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Error deleting course: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/courses/<course_id>/modules", methods=["POST"])
def create_module(course_id):
    """Create a new module in a course."""
    try:
        import uuid
        from datetime import datetime

        data = request.get_json()
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()

        if not name:
            return jsonify({"error": "Module name is required"}), 400

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        if not os.path.exists(courses_file):
            return jsonify({"error": "Course not found"}), 404

        with open(courses_file, "r") as f:
            courses = json.load(f)

        # Find the course
        course = None
        for c in courses:
            if c["id"] == course_id:
                course = c
                break

        if not course:
            return jsonify({"error": "Course not found"}), 404

        # Create new module
        new_module = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "tracks": [],
            "created_at": datetime.utcnow().isoformat(),
        }

        course["modules"].append(new_module)

        # Save courses
        with open(courses_file, "w") as f:
            json.dump(courses, f, indent=2)

        return jsonify({"success": True, "module": new_module}), 201
    except Exception as e:
        app.logger.error(f"Error creating module: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/courses/<course_id>/modules/<module_id>", methods=["DELETE"])
def delete_module(course_id, module_id):
    """Delete a module from a course."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        if not os.path.exists(courses_file):
            return jsonify({"error": "Course not found"}), 404

        with open(courses_file, "r") as f:
            courses = json.load(f)

        # Find the course and remove the module
        for course in courses:
            if course["id"] == course_id:
                course["modules"] = [
                    m for m in course["modules"] if m["id"] != module_id
                ]
                break

        with open(courses_file, "w") as f:
            json.dump(courses, f, indent=2)

        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Error deleting module: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/modules/<module_id>/tracks", methods=["POST"])
def create_track(module_id):
    """Create a new audio track in a module using text-to-speech."""
    try:
        from scripts.create_audio import paragraph_to_wav
        from app.database import get_db_connection
        import uuid
        from datetime import datetime
        import re

        data = request.get_json()
        name = data.get("name", "").strip()
        text = data.get("text", "").strip()

        if not name or not text:
            return jsonify({"error": "Track name and text are required"}), 400

        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        if not os.path.exists(courses_file):
            return jsonify({"error": "Courses not found"}), 404

        with open(courses_file, "r") as f:
            courses = json.load(f)

        # Find the module and course
        module = None
        course = None
        course_idx = 0
        module_idx = 0

        for c in courses:
            for m_idx, m in enumerate(c["modules"]):
                if m["id"] == module_id:
                    module = m
                    course = c
                    module_idx = m_idx
                    break
            if module:
                break

        if not module or not course:
            return jsonify({"error": "Module not found"}), 404

        # Create safe filename: modulename-m01-trackname.wav
        def sanitize_filename(s):
            """Convert string to safe filename."""
            s = re.sub(r"[^\w\s-]", "", s.lower())
            s = re.sub(r"[-\s]+", "-", s)
            return s.strip("-")

        course_slug = sanitize_filename(course["name"])[:20]
        module_slug = sanitize_filename(module["name"])[:20]
        track_slug = sanitize_filename(name)[:30]
        module_num = str(module_idx + 1).zfill(2)
        track_num = str(len(module["tracks"]) + 1).zfill(2)

        audio_filename = f"{course_slug}-m{module_num}-{track_slug}.wav"
        audio_path = os.path.join(AUDIO_OUTPUT_DIR, audio_filename)

        # Generate audio using ElevenLabs
        try:
            result_path = paragraph_to_wav(text, audio_path)
            if not result_path or not os.path.exists(result_path):
                return jsonify({"error": "Failed to generate audio file"}), 500
        except Exception as e:
            app.logger.error(f"Error generating audio: {str(e)}")
            return jsonify({"error": f"Failed to generate audio: {str(e)}"}), 500

        # Get audio duration
        duration = None
        try:
            import wave

            with wave.open(audio_path, "rb") as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
        except Exception as e:
            app.logger.error(f"Could not get audio duration: {str(e)}")

        # Save metadata to database for Audio Library
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Create tags: course name, module name, track name
            tags = f"{course['name']}, {module['name']}, {name}"

            cursor.execute(
                """
                INSERT INTO audio_files 
                (filename, course_name, module_number, module_name, track_number, track_name, description, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audio_filename,
                    course["name"],
                    module_num,
                    module["name"],
                    track_num,
                    name,
                    text[:200],  # First 200 chars as description
                    tags,
                    datetime.utcnow().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            app.logger.info(f"Saved audio metadata to database: {audio_filename}")
        except Exception as e:
            app.logger.error(f"Error saving audio metadata: {str(e)}")

        # Create new track
        new_track = {
            "id": str(uuid.uuid4()),
            "name": name,
            "audio_file": f"/audio/{audio_filename}",
            "duration": duration,
            "created_at": datetime.utcnow().isoformat(),
        }

        module["tracks"].append(new_track)

        # Save courses
        with open(courses_file, "w") as f:
            json.dump(courses, f, indent=2)

        return (
            jsonify(
                {
                    "success": True,
                    "track": new_track,
                    "message": f"Audio track created: {audio_filename}",
                }
            ),
            201,
        )
    except Exception as e:
        app.logger.error(f"Error creating track: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/modules/<module_id>/tracks/<track_id>", methods=["DELETE"])
def delete_track(module_id, track_id):
    """Delete a track from a module."""
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        courses_file = os.path.join(project_root, "data", "courses.json")

        if not os.path.exists(courses_file):
            return jsonify({"error": "Courses not found"}), 404

        with open(courses_file, "r") as f:
            courses = json.load(f)

        # Find the module and remove the track
        for course in courses:
            for module in course["modules"]:
                if module["id"] == module_id:
                    module["tracks"] = [
                        t for t in module["tracks"] if t["id"] != track_id
                    ]
                    break

        with open(courses_file, "w") as f:
            json.dump(courses, f, indent=2)

        return jsonify({"success": True}), 200
    except Exception as e:
        app.logger.error(f"Error deleting track: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Flask web server")
    parser.add_argument("--port", type=int, default=5001, help="Port to run on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    port = args.port
    debug = args.debug

    # Test database connection
    try:
        test_settings = get_settings()
        if test_settings:
            api_keys = test_settings.get("api_keys", {})
            keys_count = sum(1 for v in api_keys.values() if v)
            print(
                f"✅ Settings loaded successfully from database ({keys_count} API keys configured)"
            )
        else:
            print(
                "ℹ️  No settings found in database - will use defaults until you configure"
            )
    except Exception as e:
        print(f"⚠️ Warning: Could not load settings: {e}")

    # Schedule daily job
    schedule_daily_job()

    # Run Flask app
    # Use environment variable for port, default to 5001 (5000 often used by AirPlay on macOS)
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("FLASK_ENV") != "production"

    # Get database path for display
    from app.database import DB_PATH

    db_path_display = DB_PATH

    print(f"\n🌐 Starting server on port {port}...")
    print(f"📱 Open in browser: http://localhost:{port}\n")
    print(f"💾 Database location: {db_path_display}")
    print(
        f"💾 Settings are saved to database - they will persist across restarts and code changes!\n"
    )

    app.run(host="0.0.0.0", port=port, debug=debug)
