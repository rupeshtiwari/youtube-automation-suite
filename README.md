# YouTube Automation Suite

A comprehensive Python toolkit for automating YouTube content management and social media distribution. Export playlists, schedule videos, and automatically post to LinkedIn, Facebook, and Instagram.

## 🚀 Features

- **Web Interface**: Beautiful web dashboard for configuration and monitoring
- **Daily Automation**: Automatically run tasks on schedule (configurable)
- **YouTube Playlist Export**: Export all playlists and videos to Excel with metadata
- **YouTube Shorts Export**: Specialized export for Shorts playlists with social media post generation
- **Video Scheduling**: Automatically reschedule all videos in a playlist to publish on specific days/times
- **Social Media Integration**: Auto-generate and post content to LinkedIn, Facebook, and Instagram
- **Smart Content Analysis**: Automatically derive video type (leadership/sys design) and role (dir/mgr/vp/sa)
- **Excel-Based Workflow**: Manage everything through Excel files for easy editing and tracking

## 📋 Prerequisites

- Python 3.8 or higher
- Google Cloud Console account with YouTube Data API v3 enabled
- OAuth 2.0 credentials for YouTube API
- (Optional) Social media API credentials for automated posting

## 🛠️ Installation

### Step 1: Create a Virtual Environment

```bash
python3 -m venv .venv
```

### Step 2: Activate the Virtual Environment

```bash
source .venv/bin/activate
```

Your prompt should now show:
```text
(.venv) ➜ youtube-automation
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable **YouTube Data API v3**
4. Go to **APIs & Services** → **Credentials**
5. Create **OAuth 2.0 Client ID** (Desktop app)
6. Download the JSON file and save it as `client_secret.json` in this directory

### Step 5: (Optional) Set Up Social Media APIs

For automated posting, you'll need API credentials. Create a `.env` file in the project root:

```bash
# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_token_here
LINKEDIN_PERSON_URN=urn:li:person:xxxxx

# Facebook Graph API
FACEBOOK_PAGE_ACCESS_TOKEN=your_token_here
FACEBOOK_PAGE_ID=your_page_id_here

# Instagram Graph API
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id_here
INSTAGRAM_ACCESS_TOKEN=your_token_here

# Ayrshare (Alternative - simpler unified API)
AYRSHARE_API_KEY=your_api_key_here
```

**Note**: You can use either native APIs (LinkedIn, Facebook, Instagram) or Ayrshare's unified API. Ayrshare is simpler to set up but requires a paid account for production use.

## 📖 Usage

### Web Interface (Recommended)

The easiest way to configure and run automation is through the web interface:

```bash
# Start the web server
python app.py
```

Then open your browser to: **http://localhost:5000**

**Features:**
- **Dashboard**: View automation status, last run time, next scheduled run
- **Configuration Page**: 
  - Enter all API keys in one place
  - Configure scheduling settings (videos per day, schedule time, day of week)
  - Enable/disable automation
  - Test API connections
  - Configure social media posting

**Configuration Options:**
- Videos per day: Number of videos to process daily (1-10)
- Schedule day: Day of week to run (Monday-Sunday)
- YouTube schedule time: Time to schedule videos (IST)
- Social media schedule time: Time to post on social platforms (IST)
- Export type: All playlists or Shorts only
- Auto-post social: Enable automatic social media posting
- Platform selection: Choose LinkedIn, Facebook, Instagram

The web interface automatically:
- Saves settings to `automation_settings.json`
- Updates `.env` file for compatibility
- Schedules daily automation tasks
- Runs in background (keeps running even after closing browser)

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

#### LinkedIn
1. Create app at [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Request access to "Marketing Developer Platform"
3. Get OAuth 2.0 access token
4. Get your Person URN from your profile

#### Facebook & Instagram
1. Create app at [Facebook Developers](https://developers.facebook.com/)
2. Add "Instagram Graph API" and "Pages" products
3. Get Page Access Token
4. Connect Instagram Business Account to Facebook Page
5. Get Instagram Business Account ID

#### Ayrshare (Alternative)
1. Sign up at [Ayrshare](https://www.ayrshare.com/)
2. Connect your social media accounts
3. Get API key from dashboard

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
