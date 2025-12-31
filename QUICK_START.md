# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Setup (One-time)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Get Google OAuth credentials
# - Go to https://console.cloud.google.com/
# - Enable YouTube Data API v3
# - Create OAuth 2.0 Client ID (Desktop app)
# - Download JSON → save as client_secret.json
```

### 2. Export Your Playlists

```bash
# Export all playlists
python export_playlists_videos_to_excel.py

# Export Shorts only
python export_shorts_to_excel.py
```

First run will open browser for Google OAuth → approve → Excel file created!

### 3. Schedule YouTube Videos (Optional)

```bash
export YOUTUBE_PLAYLIST_ID='PLxxxx...'
python schedule-youtube.py
```

This reschedules all videos to next Wednesday 11:00 PM IST.

### 4. Post to Social Media (Optional)

**Option A: Using Ayrshare (Easiest)**
```bash
# 1. Sign up at https://www.ayrshare.com/
# 2. Get API key
# 3. Add to .env file:
#    AYRSHARE_API_KEY=your_key_here

# 4. Post
python post_to_social_media.py \
  --excel youtube_shorts_export.xlsx \
  --platforms linkedin facebook instagram \
  --use-ayrshare
```

**Option B: Using Native APIs**
```bash
# 1. Set up LinkedIn, Facebook, Instagram APIs
# 2. Add credentials to .env file
# 3. Post
python post_to_social_media.py \
  --excel youtube_shorts_export.xlsx \
  --platforms linkedin facebook instagram
```

## 📝 Common Commands

```bash
# Dry run (preview without posting)
python post_to_social_media.py \
  --excel youtube_shorts_export.xlsx \
  --platforms linkedin \
  --dry-run

# Post specific rows
python post_to_social_media.py \
  --excel youtube_shorts_export.xlsx \
  --platforms linkedin \
  --start-row 0 \
  --end-row 10

# Post to specific sheet
python post_to_social_media.py \
  --excel youtube_shorts_export.xlsx \
  --platforms linkedin \
  --sheet "My Playlist Name"
```

## 🔑 Environment Variables

Create a `.env` file in the project root:

```bash
# For social media posting (optional)
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_URN=urn:li:person:xxxxx
FACEBOOK_PAGE_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_token
AYRSHARE_API_KEY=your_key

# For video scheduling
YOUTUBE_PLAYLIST_ID=PLxxxx...
```

## ❓ Troubleshooting

**"Missing client_secret.json"**
→ Download from Google Cloud Console

**"No channel found"**
→ Check you're logged into correct Google account

**"Social media credentials not configured"**
→ Either set up native APIs or use `--use-ayrshare` flag

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Customize post generation in Excel files
- Set up automated posting schedules

