# YouTube Automation Suite - Cross-Channel Publishing Platform

> **Publish YouTube shorts to multiple channels at once—just like Buffer.com!**

A complete automation platform for creating, scheduling, and publishing video shorts across YouTube, Facebook, Instagram, and LinkedIn.

## 🚀 Quick Start

```bash
# 1. Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Start
python run.py

# 3. Open
Visit http://localhost:5001
```

## ✨ What You Can Do

- 📱 **Upload shorts** to your library
- 🎯 **Generate captions** automatically (AI-powered)
- 📅 **Schedule to multiple channels** - YouTube, Facebook, Instagram, LinkedIn
- 📊 **Track analytics** - views, engagement, audience insights
- 🤖 **Automate publishing** - schedule once, publish everywhere

## 📚 Documentation

**Start here based on your needs:**

| I want to...                | Read this                                              |
| --------------------------- | ------------------------------------------------------ |
| Learn how to publish shorts | [📖 HOW_TO_PUBLISH_SHORTS.md](HOW_TO_PUBLISH_SHORTS.md) |
| Setup the app (5 min)       | [🚀 QUICK_START.md](QUICK_START.md)                     |
| Understand all features     | [📘 README_MAIN.md](README_MAIN.md)                     |
| Configure OAuth & API keys  | [⚙️ CONFIG_STATUS.md](CONFIG_STATUS.md)                 |
| Setup on server/NAS         | [🖥️ DEPLOY_NAS.md](DEPLOY_NAS.md)                       |

## 🎯 Core Features

### 1. Upload & Manage
- Upload short videos (≤60 seconds)
- Organize by playlists
- Preview before publishing

### 2. Generate & Edit
- AI-powered caption generation
- Edit captions & tags
- Custom templates

### 3. Schedule Everywhere
```
Select Video → Choose Channels → Pick Time → Publish
```
Automatically publishes to:
- ✅ YouTube
- ✅ Facebook
- ✅ Instagram
- ✅ LinkedIn

### 4. Analytics & Insights
- Views, likes, shares per platform
- Audience demographics
- Optimal posting times
- Content performance trends

### 5. Automation
- Daily automated publishing
- Batch scheduling
- Intelligent retries
- Activity logging

## 🔗 Supported Platforms

| Platform    | Status         |
| ----------- | -------------- |
| 🎬 YouTube   | ✅ Full Support |
| 📘 Facebook  | ✅ Full Support |
| 📷 Instagram | ✅ Full Support |
| 💼 LinkedIn  | ✅ Full Support |
| 𝕏 Twitter   | 🔜 Coming Soon  |

## 🛠️ Tech Stack

- **Backend**: Python + Flask
- **Frontend**: React + TypeScript + TailwindCSS
- **Database**: SQLite
- **Scheduling**: APScheduler
- **APIs**: YouTube v3, Facebook Graph, LinkedIn OAuth

## ⚙️ Setup Checklist

- [ ] Install Python 3.8+
- [ ] Create virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Start app: `python run.py`
- [ ] Open http://localhost:5001
- [ ] Go to Settings ⚙️
- [ ] Connect YouTube (🎬 Connect)
- [ ] Connect Facebook (📘 Connect)
- [ ] Start publishing! 🎉

## 🎓 Example Workflow

```
1. Upload Video
   Shorts → Upload → Select file → Save

2. Generate Caption
   Your Video → Generate Caption → Edit → Save

3. Schedule to Channels
   Queue → Your Video → ➕ Publish
   Select: YouTube ✓ Facebook ✓ Instagram
   Pick time → Schedule Publishing

4. Track Performance
   Analytics → See views & engagement
```

Done! Your short publishes automatically to all channels ✨

## 📊 Dashboard Overview

### 📅 Queue
- All pending, scheduled, published content
- Real-time status updates
- One-click publishing

### 🗓️ Calendar
- Visual timeline of all posts
- Drag-to-reschedule
- Multi-platform view

### 🎬 Shorts
- Upload & manage videos
- Generate captions
- Bulk operations

### 📊 Analytics
- Performance metrics
- Optimal posting times
- Audience insights

### ⚙️ Settings
- Connect channels
- API configuration
- Automation rules

## 🐛 Troubleshooting

**Video won't upload?**
- Check file size (max 128MB)
- Verify it's a valid video format
- Ensure audio codec is AAC or MP3

**Publishing failed?**
- Check internet connection
- Verify channels are connected in Settings
- Check if you've hit YouTube quota (6/day)

**Channels not showing?**
- Go to Settings → Reconnect the platform
- Refresh page (F5)
- Clear browser cache

**More help?** See [HOW_TO_PUBLISH_SHORTS.md → Troubleshooting](HOW_TO_PUBLISH_SHORTS.md#-troubleshooting)

## 🎯 Pro Tips

1. **Post at off-peak times** - Less competition, more visibility
2. **Repurpose content** - Cut one long video into multiple shorts
3. **Use caption templates** - Save time, keep consistency
4. **Schedule in batches** - Do a week's worth in one session
5. **Monitor analytics** - See what works, double down on it

## 📞 Need Help?

1. **Check Docs**: [HOW_TO_PUBLISH_SHORTS.md](HOW_TO_PUBLISH_SHORTS.md) has complete guide + FAQ
2. **Check Logs**: Terminal shows detailed error messages
3. **Restart App**: Kill process and start fresh
4. **Clear Cache**: Browser cache might need clearing

## 📝 License

MIT License - feel free to use and modify!

## 🙋 FAQ

**Q: Is this safe?**  
A: Yes! Tokens stored locally only, official OAuth used, no data shared.

**Q: Can I run on a server?**  
A: Yes! Docker & NAS supported. See DEPLOY_NAS.md.

**Q: Upload limits?**  
A: YouTube: 6/day. Facebook/Instagram/LinkedIn: Unlimited.

**Q: Can I schedule months ahead?**  
A: Yes! Schedule as far ahead as you want.

---

**Ready to start?** → [📖 HOW_TO_PUBLISH_SHORTS.md](HOW_TO_PUBLISH_SHORTS.md)

*Version 2.0 - Cross-Channel Publishing Release*  
*Last Updated: January 2026*

2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**
4. Go to **APIs & Services** → **Credentials**
5. Create **OAuth 2.0 Client ID** (Desktop app)
6. Download the JSON file and save it as `client_secret.json` in this directory

### Step 5: (Optional) Set Up Social Media APIs

For automated posting, you'll need API credentials. 

**📖 Complete Setup Guide:** See [API_KEYS_SETUP.md](API_KEYS_SETUP.md) for detailed step-by-step instructions on getting all API keys.

**Quick Overview:**
- **LinkedIn**: Get access token from [LinkedIn Developers](https://www.linkedin.com/developers/)
- **Facebook**: Get page access token from [Facebook Developers](https://developers.facebook.com/)
- **Instagram**: Use Facebook Graph API (requires Instagram Business Account)
- **Ayrshare**: Sign up at [Ayrshare.com](https://www.ayrshare.com/) - easiest option!

**Configuration Options:**
1. **Via Web Interface** (Recommended): Enter all keys in the Configuration page
2. **Via .env file**: Create `.env` file in project root (see `API_KEYS_SETUP.md` for format)

**Note**: You can use either native APIs (LinkedIn, Facebook, Instagram) or Ayrshare's unified API. Ayrshare is simpler to set up and handles Instagram images automatically.

## 📖 Usage

### Web Interface (Recommended)

The easiest way to configure and run automation is through the web interface:

```bash
# Start the web server
python app.py
```

Then open your browser to: **http://localhost:5001**

**Available Pages:**
- **📊 Dashboard** (`/`): Overview of automation status, quick actions, recent activity
- **📋 Playlists** (`/playlists`): View all YouTube playlists and videos with social media posts
- **📅 Calendar** (`/calendar`): Visual calendar view of scheduled posts (Buffer.com style)
- **⚙️ Configuration** (`/config`): Set API keys, scheduling preferences, automation settings
- **📚 Documentation** (`/docs`): Complete UI documentation and guides

**Key Features:**
- **Dashboard**: View automation status, last run time, next scheduled run
- **Playlists Page**: Browse all playlists, videos, thumbnails, and social media posts
- **Calendar View**: Visual calendar with color-coded scheduled posts across platforms
- **Configuration Page**: 
  - Enter all API keys in one place
  - Configure scheduling settings (videos per day, schedule time, day of week)
  - Enable/disable automation
  - Test API connections
  - Configure social media posting
- **Built-in Documentation**: Complete user guide accessible from the UI

**Configuration Options:**
- Videos per day: Number of videos to process daily (1-10)
- Schedule day: Day of week to run (Monday-Sunday)
- YouTube schedule time: Time to schedule videos (IST)
- Social media schedule time: Time to post on social platforms (IST)
- Export type: All playlists or Shorts only
- Auto-post social: Enable automatic social media posting
- Platform selection: Choose LinkedIn, Facebook, Instagram
- Storage: Choose between SQLite database or Excel files

The web interface automatically:
- Saves settings to `automation_settings.json`
- Updates `.env` file for compatibility
- Schedules daily automation tasks
- Runs in background (keeps running even after closing browser)

**📖 For complete UI documentation, see [UI_DOCUMENTATION.md](./UI_DOCUMENTATION.md) or click "Documentation" in the web interface.**

### Command Line Usage

### 1. Export All Playlists to Excel

Export all playlists and videos with generated social media posts:

```bash
python export_playlists_videos_to_excel.py
```

This creates `youtube_playlists_videos_export.xlsx` with:
- Video metadata (title, description, tags, dates)
- Derived type (leadership/sys design) and role (dir/mgr/vp/sa)
- Generated LinkedIn, Facebook, and Instagram posts
- One sheet per playlist

### 2. Export YouTube Shorts to Excel

Export Shorts playlists with enhanced social media scheduling:

```bash
python export_shorts_to_excel.py
```

This creates `youtube_shorts_export.xlsx` with:
- All fields from regular export
- Calculated schedule dates (Wednesdays at 7:30pm IST starting Jan 7, 2025)
- Status tracking fields (pending/scheduled/error)
- YouTube URLs for reference

### 3. Schedule YouTube Videos

Reschedule all videos in a playlist to publish on the next Wednesday at 11:00 PM IST:

```bash
export YOUTUBE_PLAYLIST_ID='PLxxxx...'
python schedule-youtube.py
```

The script will:
- Find all videos in the specified playlist
- Update their publish time to the next Wednesday 11:00 PM IST
- Set privacy status to "private" (required for scheduling)

### 4. Post to Social Media

Post content from Excel file to social media platforms:

```bash
# Post to all platforms
python post_to_social_media.py --excel youtube_shorts_export.xlsx --platforms linkedin facebook instagram

# Post to specific platform only
python post_to_social_media.py --excel youtube_shorts_export.xlsx --platforms linkedin

# Dry run (preview without posting)
python post_to_social_media.py --excel youtube_shorts_export.xlsx --platforms linkedin facebook instagram --dry-run

# Use Ayrshare API instead of native APIs
python post_to_social_media.py --excel youtube_shorts_export.xlsx --platforms linkedin facebook instagram --use-ayrshare

# Post specific rows
python post_to_social_media.py --excel youtube_shorts_export.xlsx --platforms linkedin --start-row 0 --end-row 10
```

The script will:
- Read posts from Excel file
- Post to specified platforms
- Update Excel with actual scheduled dates and status
- Skip already posted/scheduled items

## 📁 Project Structure

```
youtube-automation/
├── app.py                                 # Flask web application
├── templates/                             # HTML templates
│   ├── base.html                          # Base template
│   ├── dashboard.html                     # Dashboard page
│   └── config.html                        # Configuration page
├── export_playlists_videos_to_excel.py    # Export all playlists
├── export_shorts_to_excel.py              # Export Shorts with scheduling
├── schedule-youtube.py                    # Reschedule videos
├── post_to_social_media.py                # Post to social media
├── requirements.txt                        # Python dependencies
├── automation_settings.json               # Web interface settings (auto-generated)
├── client_secret.json                     # Google OAuth credentials (not in repo)
├── token.json                             # OAuth token cache (auto-generated)
├── .env                                   # Social media API keys (not in repo)
└── README.md                              # This file
```

## 🔧 Configuration

### YouTube API Scopes

- `youtube.readonly`: For exporting playlists and videos
- `youtube.force-ssl`: For scheduling and updating videos

### Social Media API Setup

**📖 For detailed step-by-step instructions, see [API_KEYS_SETUP.md](API_KEYS_SETUP.md)**

**Quick Links:**
- **LinkedIn**: [LinkedIn Developers](https://www.linkedin.com/developers/) - Request Marketing Developer Platform access
- **Facebook**: [Facebook Developers](https://developers.facebook.com/) - Create app, add Pages product
- **Instagram**: Requires Facebook Page + Instagram Business Account
- **Ayrshare**: [Ayrshare.com](https://www.ayrshare.com/) - Easiest option, unified API for all platforms

**Recommended Approach:**
1. Start with **Ayrshare** (simplest, handles everything)
2. Or use native APIs for more control (see detailed guide)

## 📊 Excel File Format

### Regular Export (`youtube_playlists_videos_export.xlsx`)
- **Video Name**: YouTube video ID
- **Title**: Video title
- **Description**: Full video description
- **Tags**: Comma-separated tags
- **Schedule/Published Date**: Publish date
- **Type**: Derived type (leadership/sys design)
- **Role**: Derived role (dir/mgr/vp/sa)
- **LinkedIn Post**: Generated LinkedIn post text
- **Facebook Post**: Generated Facebook post text
- **Instagram Post**: Generated Instagram post text

### Shorts Export (`youtube_shorts_export.xlsx`)
All fields from regular export, plus:
- **YouTube Schedule/Published Date**: YouTube publish date
- **Privacy Status**: Video privacy status
- **LinkedIn/Facebook/Instagram Schedule Date**: Calculated schedule dates
- **LinkedIn/Facebook/Instagram Actual Scheduled Date**: Updated after posting
- **LinkedIn/Facebook/Instagram Status**: pending/scheduled/error
- **YouTube URL**: Direct link to video

## 🎯 Content Generation

The scripts automatically generate social media posts based on:
- Video title and description
- Derived type (leadership vs system design)
- Derived role (director, manager, VP, senior architect)
- Content analysis (topics, pain points, value propositions)

Posts are optimized for each platform:
- **LinkedIn**: Professional, SEO-optimized, engaging
- **Facebook**: Casual, viral-style, shareable
- **Instagram**: Visual, emoji-rich, hashtag-optimized

## ⚠️ Troubleshooting

### "Missing client_secret.json"
- Download OAuth credentials from Google Cloud Console
- Save as `client_secret.json` in project root

### "No channel found"
- Make sure you're logged into the correct Google account
- Check that YouTube Data API v3 is enabled

### "LinkedIn/Facebook/Instagram credentials not configured"
- Create `.env` file with API credentials
- Or use `--use-ayrshare` flag with Ayrshare API key

### "Instagram requires an image"
- Instagram posts require an image
- Use Ayrshare API which handles this automatically
- Or provide image URLs in the posting script

### Rate Limiting
- APIs have rate limits
- Scripts include automatic retries and delays
- If you hit limits, wait a few minutes and retry

## 🔒 Security Notes

- Never commit `client_secret.json`, `token.json`, or `.env` to version control
- These files are already in `.gitignore`
- Rotate API keys regularly
- Use environment variables for production deployments

## 📝 License

This project is provided as-is for personal and commercial use.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📞 Support

For questions or issues:
- Check the troubleshooting section above
- Review API documentation for each platform
- Ensure all credentials are correctly configured

---

**Happy Automating! 🚀**
