# YouTube Automation Suite - UI Documentation

Complete guide to using the web interface for YouTube Automation Suite.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Playlists & Videos](#playlists--videos)
4. [Calendar View](#calendar-view)
5. [Configuration](#configuration)
6. [API Key Setup](#api-key-setup)
7. [Automation Settings](#automation-settings)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Web Interface

1. **Start the Server**
   ```bash
   ./run_local.sh
   # Or manually:
   source .venv/bin/activate
   python3 app.py
   ```

2. **Open in Browser**
   - Local: http://localhost:5001
   - Network: http://YOUR_IP:5001

3. **Initial Setup**
   - First time: Configure API keys in the Configuration page
   - Set up scheduling preferences
   - Enable automation

---

## Dashboard

**URL:** `/` or `/dashboard`

### Overview

The dashboard provides a central overview of your automation system.

### Features

#### Status Cards
- **Automation Status**: Shows if daily automation is enabled/disabled
- **Last Run**: Timestamp of the last automation execution
- **Next Run**: When the next scheduled run will occur
- **Database Status**: Whether SQLite database is active

#### Quick Actions
- **Run Now**: Manually trigger automation immediately
- **View Playlists**: Link to playlists page
- **View Calendar**: Link to calendar view
- **Configure**: Link to configuration page

#### Recent Activity
- Shows recent automation runs
- Displays success/error status
- Links to detailed logs

### Navigation Menu

Top navigation bar provides quick access to:
- 🏠 **Dashboard**: Home page overview
- 📋 **Playlists**: View all playlists and videos
- 📅 **Calendar**: Calendar view of scheduled posts
- ⚙️ **Configuration**: Settings and API keys

---

## Playlists & Videos

**URL:** `/playlists`

### Purpose

View all your YouTube playlists, videos, and their associated social media posts in one place.

### Features

#### Playlist List
- **Playlist Cards**: Each playlist shown as an expandable card
- **Playlist Metadata**:
  - Title and description
  - Number of videos
  - Published date
  - Direct link to YouTube playlist
  - Thumbnail

#### Video Details
For each video, you can see:

1. **Video Information**
   - Title (clickable link to YouTube)
   - Thumbnail image
   - Published date
   - Scheduled publish date (if private/scheduled)
   - Privacy status (Public/Private/Unlisted)
   - Tags

2. **Social Media Posts**
   - **LinkedIn Post**
     - Post content text
     - Schedule date
     - Status (pending/scheduled/posted/error)
   - **Facebook Post**
     - Post content text
     - Schedule date
     - Status
   - **Instagram Post**
     - Post content text
     - Schedule date
     - Status

#### Status Badges

- 🟡 **Pending**: Post is queued but not yet scheduled
- 🟢 **Scheduled**: Post is scheduled on the platform
- 🔴 **Error**: Post failed to schedule
- ⚪ **Posted**: Post has been published

### How to Use

1. **View Playlists**
   - Page loads all playlists automatically
   - Click playlist header to expand/collapse
   - First playlist is expanded by default

2. **Navigate Videos**
   - Scroll through videos in each playlist
   - Click video title to open on YouTube
   - Click "Watch" button for direct video access

3. **Check Social Posts**
   - Expand playlist to see video social media posts
   - Review post content and scheduling dates
   - Verify status for each platform

4. **Performance Note**
   - Only first 10 playlists load videos by default
   - This prevents slow page loads
   - Click individual playlists to load their videos

---

## Calendar View

**URL:** `/calendar`

### Purpose

Visual calendar representation of all scheduled social media posts, similar to Buffer.com's calendar interface.

### Features

#### Calendar Interface

1. **Views**
   - **Month View**: Overview of entire month
   - **Week View**: Detailed weekly schedule
   - **Day View**: Hour-by-hour breakdown

2. **Event Display**
   - Color-coded by platform:
     - 🔵 **LinkedIn**: Blue (#0077b5)
     - 🔵 **Facebook**: Blue (#1877f2)
     - 🔴 **Instagram**: Pink (#e4405f)
   - Event title shows: `Platform: Video Title`
   - Status indicated by opacity (pending = lighter)

3. **Navigation**
   - Previous/Next buttons to navigate months
   - "Today" button to jump to current date
   - Click dates to jump to specific days

#### Event Details Modal

Click any event to see:

- **Platform**: Which social network
- **Video Title**: Full title with YouTube link
- **Scheduled Time**: Exact date and time
- **Status**: Current post status
- **Post Content**: Full text of the post
- **Action**: Link to view video on YouTube

### How to Use

1. **Navigate Calendar**
   - Use arrows to move between months
   - Click "Today" to return to current date
   - Switch views using top-right buttons

2. **View Events**
   - Hover over events to see quick preview
   - Click event for full details
   - Multiple events on same day stack vertically

3. **Filter by Platform**
   - Events are color-coded
   - Use legend to identify platforms
   - Each platform has distinct color

4. **Check Schedules**
   - Verify all posts are scheduled correctly
   - Spot scheduling conflicts
   - Plan future content

---

## Configuration

**URL:** `/config`

### Purpose

Configure API keys, scheduling preferences, and automation settings.

### Sections

#### 1. API Keys

**Social Media APIs**

- **LinkedIn**
  - Access Token
  - Person URN (User ID)
  - How to get: See [API_KEYS_SETUP.md](./API_KEYS_SETUP.md)

- **Facebook**
  - Page Access Token
  - Page ID
  - How to get: See [API_KEYS_SETUP.md](./API_KEYS_SETUP.md)

- **Instagram**
  - Business Account ID
  - Access Token
  - How to get: See [API_KEYS_SETUP.md](./API_KEYS_SETUP.md)

**Ayrshare (Alternative)**

- **API Key**: Single key for all platforms
- Use Ayrshare instead of individual APIs
- Simpler setup, unified posting

**Testing APIs**

- Click "Test Connection" buttons to verify API keys
- Shows success/error messages
- Tests authentication without posting

#### 2. Scheduling Settings

**Automation Toggle**
- Enable/disable daily automation
- When disabled, automation won't run

**Videos Per Day**
- Number of videos to process daily
- Default: 1 video per day
- Range: 1-10 recommended

**Schedule Times**

- **YouTube Schedule Time**: When to schedule videos on YouTube
  - Format: HH:MM (24-hour)
  - Example: 23:00 (11:00 PM)
  - Default: 23:00

- **Social Media Schedule Time**: When to schedule social posts
  - Format: HH:MM (24-hour)
  - Example: 19:30 (7:30 PM)
  - Default: 19:30

**Schedule Day**
- Day of week to run automation
- Options: Monday through Sunday
- Default: Wednesday

**Playlist ID**
- YouTube playlist ID to process
- Find in playlist URL: `list=PLAYLIST_ID`
- Leave empty to use default

**Export Type**
- **shorts**: Process Shorts playlists only
- **all**: Process all playlists
- Default: shorts

#### 3. Storage Options

**Database Toggle**
- **Use Database**: Store data in SQLite (recommended)
  - Better performance
  - Concurrent access
  - Query capabilities
- **Use Excel**: Store data in Excel files (legacy)
  - Easier manual editing
  - Spreadsheet view

### How to Use

1. **Configure API Keys**
   ```
   Step 1: Get API keys (see API_KEYS_SETUP.md)
   Step 2: Paste keys into fields
   Step 3: Click "Test Connection" to verify
   Step 4: Click "Save Configuration"
   ```

2. **Set Scheduling**
   ```
   Step 1: Enable automation toggle
   Step 2: Set videos per day
   Step 3: Choose schedule times
   Step 4: Select schedule day
   Step 5: Enter playlist ID (optional)
   Step 6: Click "Save Configuration"
   ```

3. **Save Changes**
   - Always click "Save Configuration" after changes
   - Changes are saved to `automation_settings.json`
   - `.env` file is also updated
   - Automation reloads with new settings

---

## API Key Setup

### Quick Links

For detailed API key setup instructions, see:
- **[API_KEYS_SETUP.md](./API_KEYS_SETUP.md)**: Complete guide for all platforms

### Overview

1. **LinkedIn**
   - Create LinkedIn App
   - Get OAuth tokens
   - Generate Person URN

2. **Facebook**
   - Create Facebook App
   - Get Page Access Token
   - Find Page ID

3. **Instagram**
   - Connect Instagram Business Account
   - Link to Facebook Page
   - Get Access Token

4. **Ayrshare** (Alternative)
   - Sign up at ayrshare.com
   - Get API key
   - Use instead of individual APIs

---

## Automation Settings

### How Automation Works

1. **Daily Job**
   - Runs at specified day/time
   - Fetches videos from YouTube playlist
   - Generates social media posts
   - Schedules posts on platforms

2. **Process Flow**
   ```
   Fetch Playlist → Get Videos → Generate Posts → 
   Schedule YouTube → Schedule Social Media → Save to DB/Excel
   ```

3. **Error Handling**
   - Failed posts are logged
   - Status updated in database
   - Can retry manually

### Manual Execution

From Dashboard:
1. Click "Run Now" button
2. Automation runs in background
3. Check status in dashboard
4. View results in playlists/calendar

---

## Troubleshooting

### Common Issues

#### 1. "YouTube API not configured"
**Problem**: Can't access playlists page

**Solution**:
- Ensure `client_secret.json` exists in project root
- Run YouTube export scripts to authenticate
- Check `token.json` exists

#### 2. "Could not find your YouTube channel"
**Problem**: Authentication error

**Solution**:
- Delete `token.json`
- Re-run authentication flow
- Use correct Google account

#### 3. Calendar shows no events
**Problem**: Empty calendar

**Solution**:
- Run automation or export scripts first
- Check database/Excel has data
- Verify schedule dates are set

#### 4. API Test fails
**Problem**: Connection test errors

**Solution**:
- Verify API keys are correct
- Check tokens haven't expired
- Re-generate keys if needed
- See API_KEYS_SETUP.md for details

#### 5. Server won't start
**Problem**: Port 5001 already in use

**Solution**:
```bash
# Find process using port
lsof -i :5001

# Kill process
kill -9 <PID>

# Or use different port
PORT=5002 python3 app.py
```

#### 6. Slow page loads
**Problem**: Playlists page loads slowly

**Solution**:
- Only first 10 playlists load by default
- Click individual playlists to load
- Consider using database instead of Excel

### Getting Help

1. **Check Logs**
   - Server logs in terminal
   - Database logs in `automation_runs` table
   - Error messages in UI

2. **Verify Configuration**
   - Check API keys are saved
   - Verify scheduling settings
   - Ensure automation is enabled

3. **Test Components**
   - Use "Test Connection" buttons
   - Run manual execution
   - Check database/Excel files

---

## Keyboard Shortcuts

- `Ctrl/Cmd + K`: Quick search (if implemented)
- `Esc`: Close modals
- Arrow keys: Navigate calendar (in calendar view)

---

## Best Practices

### 1. Regular Monitoring
- Check dashboard daily
- Review calendar weekly
- Monitor automation runs

### 2. Backup Settings
- Export `automation_settings.json`
- Backup database files
- Keep API keys secure

### 3. Schedule Planning
- Use calendar to plan content
- Avoid scheduling conflicts
- Balance posting times

### 4. API Key Security
- Never commit keys to Git
- Use environment variables
- Rotate keys periodically

---

## Feature Roadmap

### Current Features
- ✅ Dashboard overview
- ✅ Playlists & videos view
- ✅ Calendar view
- ✅ Configuration management
- ✅ API key testing
- ✅ Manual automation triggers

### Future Enhancements
- ⏳ Bulk operations
- ⏳ Post editing in UI
- ⏳ Analytics dashboard
- ⏳ Export reports
- ⏳ Multi-account support
- ⏳ Mobile responsive improvements

---

## Support & Resources

- **Documentation**: See README.md
- **API Setup**: See API_KEYS_SETUP.md
- **Database Guide**: See DATABASE_GUIDE.md
- **Deployment**: See NAS_DEPLOYMENT.md

---

**Last Updated**: January 2026
**Version**: 1.0

