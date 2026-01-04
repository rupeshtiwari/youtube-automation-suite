# YouTube Automation Suite - Directory Structure

## 📁 Project Organization

This project follows industry-standard directory structure for better maintainability.

### Root Directory
```
youtube-automation/
├── app/                    # Main application code
├── frontend/               # React frontend application
├── scripts/                # Automation and utility scripts
├── docs/                   # Documentation files
├── config/                 # Configuration files
├── data/                   # Data storage
├── static/                 # Static assets
├── templates/              # HTML templates
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # Main README
```

### Directory Purposes

#### `/app` - Application Code
- **Purpose:** Core application logic
- **Contains:** Flask routes, database models, API integrations
- **Key Files:**
  - `main.py` - Main Flask application
  - `database.py` - Database operations
  - `facebook_token_helper.py` - Facebook OAuth helper
  - `linkedin_token_helper.py` - LinkedIn OAuth helper

#### `/frontend` - React Frontend
- **Purpose:** User interface
- **Contains:** React components, pages, and styles
- **Key Folders:**
  - `src/pages/` - Main pages (Calendar, Settings, etc.)
  - `src/components/` - Reusable UI components
  - `src/lib/` - Utilities and helpers

#### `/scripts` - Automation Scripts
- **Purpose:** Automation, setup, and utility scripts
- **Contains:** Shell scripts (.sh) and Python utilities
- **Key Files:**
  - `auto_setup_complete.sh` - Complete setup automation
  - `build_and_run.sh` - Build and run the application
  - `one_click_setup_mac.sh` - Mac setup script
  - `verify_setup.sh` - Verify installation
  - Various Python helper scripts

#### `/docs` - Documentation
- **Purpose:** All documentation and guides
- **Contains:** Markdown files (.md) and text files
- **Key Files:**
  - `GETTING_STARTED.md` - Quick start guide
  - `HOW_TO_PUBLISH_SHORTS.md` - Publishing workflow
  - `LINKEDIN_OAUTH_FIX.md` - LinkedIn OAuth setup
  - `CALENDAR_LINKEDIN_COMPLETE.md` - Implementation summary
  - `FEATURE_SUMMARY.txt` - Complete feature list

#### `/config` - Configuration Files
- **Purpose:** Configuration and credential files
- **Contains:** JSON configuration files
- **Key Files:**
  - `client_secret.json` - Google OAuth credentials
  - `token.json` - OAuth tokens
  - `MY_CONFIG.json` - Application configuration
  - **.gitignore'd** - Sensitive files not committed to git

#### `/data` - Data Storage
- **Purpose:** Database and data files
- **Contains:** SQLite database, cached data
- **Key Files:**
  - `youtube_automation.db` - Main database
  - Temporary data files

#### `/static` - Static Assets
- **Purpose:** Static files served by Flask
- **Contains:** Images, CSS, JavaScript
- **Note:** Frontend static files are built to this directory

#### `/templates` - HTML Templates
- **Purpose:** Server-side HTML templates
- **Contains:** Jinja2 templates for Flask
- **Note:** Mostly used for backwards compatibility

---

## 🚀 Quick Commands

### Start Application
```bash
# From project root
python run.py
```

### Build Frontend
```bash
cd frontend
npm run build
cd ..
```

### Run Setup
```bash
./scripts/auto_setup_complete.sh
```

### View Documentation
```bash
# All docs are in docs/ folder
ls docs/
```

---

## 📖 Important Documentation Files

| File                                 | Purpose                       |
| ------------------------------------ | ----------------------------- |
| `docs/GETTING_STARTED.md`            | Quick start guide             |
| `docs/CALENDAR_LINKEDIN_COMPLETE.md` | Recent implementation summary |
| `docs/LINKEDIN_OAUTH_FIX.md`         | Fix LinkedIn OAuth errors     |
| `docs/HOW_TO_PUBLISH_SHORTS.md`      | Publishing workflow           |
| `docs/FEATURE_SUMMARY.txt`           | Complete feature list         |

---

## 🔧 Configuration Files

**Location:** `config/`

- `client_secret.json` - Google OAuth credentials
- `token.json` - OAuth access tokens
- `MY_CONFIG.json` - Application settings

**⚠️ Security Note:** These files contain sensitive credentials and are NOT committed to git.

---

## 📜 Available Scripts

**Location:** `scripts/`

| Script                   | Purpose                         |
| ------------------------ | ------------------------------- |
| `auto_setup_complete.sh` | Complete automated setup        |
| `build_and_run.sh`       | Build frontend and start server |
| `one_click_setup_mac.sh` | macOS one-click setup           |
| `verify_setup.sh`        | Verify installation             |
| `restart_all.sh`         | Restart application             |

---

## 🗄️ Database

**Location:** `data/youtube_automation.db`

The application uses SQLite for data persistence.

### Key Tables:
- `videos` - YouTube video metadata
- `social_media_posts` - Scheduled posts for Facebook, Instagram, LinkedIn
- `settings` - Application settings
- `playlists` - YouTube playlists

---

## 🌐 Frontend Structure

**Location:** `frontend/src/`

```
src/
├── pages/          # Main pages
│   ├── Calendar.tsx      # Calendar view
│   ├── Settings.tsx      # Settings page
│   ├── Queue.tsx         # Queue management
│   └── ...
├── components/     # Reusable components
│   ├── Sidebar.tsx
│   └── ...
└── lib/           # Utilities
    ├── api.ts          # API client
    └── ...
```

---

## 📊 Application Flow

```
User Request
    ↓
Frontend (React) → API Call → Backend (Flask)
    ↓                              ↓
Display UI                    Database Query
                                   ↓
                            External APIs
                         (YouTube, Facebook, LinkedIn)
```

---

## 🔒 Security Best Practices

1. **Never commit config files** - They're in `.gitignore`
2. **Use environment variables** - For production deployment
3. **Rotate tokens regularly** - Especially OAuth tokens
4. **Keep dependencies updated** - Run `pip install -U -r requirements.txt`

---

## 📚 Additional Resources

- **Main README:** `README.md` in project root
- **Frontend README:** `frontend/README.md`
- **Setup Instructions:** `docs/GETTING_STARTED.md`
- **Deployment Guide:** `docs/DEPLOY_*.md` files

---

## 🎯 Recent Changes

### January 4, 2026
- ✅ Organized directory structure
- ✅ Moved all `.md` files to `docs/`
- ✅ Moved all `.sh` files to `scripts/`
- ✅ Moved all `.json` config files to `config/`
- ✅ Fixed Analytics page 500 error
- ✅ Enhanced Calendar to show only Shorts
- ✅ Added cross-platform scheduling status

---

**Happy Coding! 🚀**
