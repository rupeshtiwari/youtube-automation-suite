# Project Structure

This document describes the organization of the YouTube Automation Suite codebase.

## Directory Structure

```
youtube-automation/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Flask application (renamed from app.py)
│   ├── database.py              # Database models and operations
│   ├── views.py                 # Data fetching views/helpers
│   └── tagging.py               # Video tagging and categorization
│
├── scripts/                      # CLI scripts and utilities
│   ├── __init__.py              # Package initialization
│   ├── export_playlists_videos_to_excel.py
│   ├── export_shorts_to_excel.py
│   ├── export_shorts_to_database.py
│   ├── schedule_youtube.py      # YouTube scheduling (renamed from schedule-youtube.py)
│   ├── post_to_social_media.py  # Social media posting
│   ├── migrate_to_database.py   # Database migration
│   └── deployment/              # Deployment scripts
│       ├── run_local.sh
│       ├── deploy_nas.sh
│       ├── deploy_to_your_nas.sh
│       ├── synology_one_click.sh
│       └── ... (other deployment scripts)
│
├── templates/                    # HTML templates (Flask)
│   ├── base.html
│   ├── dashboard.html
│   ├── calendar.html
│   ├── playlists.html
│   ├── config.html
│   ├── documentation.html
│   └── error.html
│
├── docs/                         # Documentation
│   ├── API_KEYS_SETUP.md
│   ├── UI_DOCUMENTATION.md
│   ├── DATABASE_GUIDE.md
│   ├── NAS_DEPLOYMENT.md
│   ├── QUICK_START.md
│   └── ... (other documentation files)
│
├── static/                       # Static assets (CSS, JS, images)
│   ├── css/
│   └── js/
│
├── data/                         # Data files (gitignored)
│   ├── youtube_automation.db    # SQLite database
│   ├── *.xlsx                   # Excel exports
│   └── automation_settings.json # App settings
│
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
├── .gitignore                   # Git ignore rules
├── README.md                    # Main project documentation
└── PROJECT_STRUCTURE.md         # This file
```

## Package Organization

### `app/` - Application Code
Contains the core Flask application and business logic:
- **main.py**: Flask app initialization, routes, and configuration
- **database.py**: SQLite database operations and models
- **views.py**: YouTube API data fetching and helpers
- **tagging.py**: Video categorization and tagging logic

### `scripts/` - CLI Scripts
Standalone scripts for various operations:
- Export scripts for Excel and database
- YouTube scheduling
- Social media posting
- Database migration
- Deployment scripts in `scripts/deployment/`

### `templates/` - HTML Templates
Flask Jinja2 templates for the web interface.

### `docs/` - Documentation
All markdown documentation files (except README.md which stays at root).

### `data/` - Data Files
Runtime data that should not be committed:
- Database files
- Excel exports
- Configuration files with sensitive data

## Import Patterns

### Within the `app/` package:
```python
from app.database import get_video
from app.views import get_youtube_service
from app.tagging import derive_type
```

### From scripts:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database
from app.tagging import derive_type
```

## Running the Application

### Development:
```bash
python3 run.py
```

### Production (Docker):
```bash
docker-compose up
```

### Individual Scripts:
```bash
python3 scripts/export_shorts_to_database.py
python3 scripts/schedule_youtube.py
```

## Best Practices

1. **Separation of Concerns**: Application code in `app/`, scripts in `scripts/`
2. **Documentation**: All docs in `docs/` folder
3. **Data Isolation**: Runtime data in `data/` (gitignored)
4. **Import Paths**: Use `app.` prefix for application modules
5. **Entry Point**: Use `run.py` as the main entry point
6. **Deployment Scripts**: Organized in `scripts/deployment/`

