# 🎬 YouTube Automation Suite - Cross-Channel Publishing Platform

> **Publish YouTube shorts to multiple channels at once—just like Buffer.com!**

A complete automation platform for creating, scheduling, and publishing video shorts across YouTube, Facebook, Instagram, and LinkedIn with a beautiful web interface.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ What Is This App?

**YouTube Automation** is a modern, Buffer.com-style content scheduling platform specifically designed for video creators who want to:

- 📱 **Create & Upload** YouTube shorts effortlessly
- 🎯 **Generate Captions** automatically using AI
- 📅 **Schedule Once, Publish Everywhere** across multiple platforms
- 🤖 **Automate Workflows** with intelligent scheduling
- 📊 **Track Performance** with detailed analytics
- 💼 **Manage Channels** - YouTube, Facebook, Instagram, LinkedIn all in one place

### 🎯 Who Is This For?

✅ **YouTube Creators** publishing shorts regularly  
✅ **Content Agencies** managing multiple channels  
✅ **Social Media Teams** automating cross-platform posting  
✅ **Businesses** maintaining consistent social presence  
✅ **Anyone** tired of uploading videos to each platform separately  

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.8+
- Google Cloud account (for YouTube API)
- Facebook/Meta account (for Facebook & Instagram)
- LinkedIn account (optional)

### Installation

```bash
# 1. Clone repository
git clone <your-repo-url>
cd youtube-automation

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the app
python run.py
```

**App opens at:** http://localhost:5001

### First Time Setup

1. **Open Settings** (⚙️ icon)
2. **Connect YouTube** → Click "Connect" → Authorize with Google
3. **Connect Facebook/Instagram** → Click "Connect" → Authorize with Meta
4. **Connect LinkedIn** (optional) → Click "Connect" → Authorize with LinkedIn

✅ **You're ready to start publishing!**

---

## 📖 Core Features

### 1️⃣ **Upload & Manage Shorts**
```
Shorts → Upload Video → App detects shorts automatically
         ↓
       Generate Caption (AI-powered)
         ↓
       Ready to Publish
```

**Features:**
- Batch upload multiple videos
- Auto-detect short format (≤60 seconds)
- Video preview before publishing
- Organize by playlists/tags

### 2️⃣ **Schedule & Cross-Publish**
```
Select Video → Choose Channels → Pick Time → Publish
                  ↓
        Auto-publishes to all at once!
        YouTube • Facebook • Instagram • LinkedIn
```

**Features:**
- Schedule to multiple channels simultaneously
- One-click publishing
- Optimal posting time recommendations
- Scheduled queue with real-time status

### 3️⃣ **Intelligent Analytics**
```
Analytics → View Performance → Optimize Strategy
```

**Metrics:**
- Views per video per platform
- Engagement rates (likes, comments, shares)
- Audience insights
- Optimal posting times
- Content performance trends

### 4️⃣ **Automation Engine**
```
Automated Tasks:
  • Daily posting schedule
  • Bulk content publishing
  • Caption generation
  • Content repurposing
```

**Features:**
- Cron-based scheduler
- Customizable automation rules
- Error handling & retries
- Activity logging

### 5️⃣ **Unified Dashboard**
```
One place to manage everything:
  • Publishing Queue
  • Calendar view
  • Analytics
  • Channel management
  • Settings & integrations
```

---

## 📱 Supported Platforms

| Platform    | Upload   | Scheduling | Analytics | Status  |
| ----------- | -------- | ---------- | --------- | ------- |
| 🎬 YouTube   | ✅ Direct | ✅ Full     | ✅ Full    | ✅ Ready |
| 📘 Facebook  | ✅ Direct | ✅ Full     | ✅ Full    | ✅ Ready |
| 📷 Instagram | ✅ Direct | ✅ Full     | ✅ Full    | ✅ Ready |
| 💼 LinkedIn  | ⚠️ Links  | ✅ Full     | ⚠️ Limited | ✅ Ready |
| 𝕏 Twitter   | 🔜 Coming | 🔜 Coming   | 🔜 Coming  | 🔜 Soon  |

---

## 🎓 How to Use

### Publishing a Short to Multiple Channels

#### **Step 1: Create Content**
```
1. Go to Shorts → Upload Video
2. Select your short (MP4, WebM, etc.)
3. App validates it's ≤60 seconds
4. Click Save
```

#### **Step 2: Generate Caption**
```
1. Click Generate Caption (magic wand ✨)
2. App creates engaging caption
3. Edit if needed
4. Save
```

#### **Step 3: Schedule to Channels**
```
1. Go to Queue (📅 icon)
2. Find your video
3. Click ➕ (Publish to Channels)
4. Select: YouTube ✓ Facebook ✓ Instagram
5. Pick date & time
6. Click Schedule Publishing
```

#### **Step 4: Done! 🎉**
```
Your short automatically publishes to:
  ✓ YouTube at scheduled time
  ✓ Facebook at scheduled time
  ✓ Instagram at scheduled time
  
Track status in the Queue!
```

### Buffer.com-Style Workflow

Just like Buffer.com makes social media easy, we make video publishing easy:

| Buffer           | YouTube Automation        |
| ---------------- | ------------------------- |
| Write post       | Create/upload short       |
| Choose platforms | Select channels           |
| Schedule time    | Pick date & time          |
| Publish auto     | Auto-publishes everywhere |
| Track analytics  | View per-platform stats   |

---

## 🎯 Main Pages & Features

### 📅 **Queue** (Home Page)
- View all pending, scheduled, and published content
- Filter by status or platform
- Quick actions: edit, reschedule, republish
- Drag-and-drop to reschedule

### 🗓️ **Calendar**
- Visual calendar of all scheduled posts
- See what's publishing when
- Click to modify schedule
- Month/week/day views

### 🎬 **Shorts**
- Upload and manage video library
- Generate captions and tags
- Preview videos
- Bulk actions

### 📊 **Analytics**
- Views, likes, shares per video
- Per-platform performance
- Audience insights
- Trending content
- Optimal posting times

### 🎥 **Sessions**
- Organize content into sessions/campaigns
- Group related videos
- Bulk scheduling for campaigns
- Session statistics

### ⚙️ **Settings**
- Connect/disconnect channels
- API configuration
- Automation rules
- Caption templates
- User preferences

---

## 🔗 Platform Integrations

### YouTube Setup
```
1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Paste into Settings → YouTube
4. Click "Connect"
5. Authorize with Google account
```
✅ Ready to publish shorts!

### Facebook / Instagram Setup
```
1. Create Facebook App at developers.facebook.com
2. Get App ID and Secret
3. Add to Settings → Facebook
4. Click "Connect"
5. Authorize with Meta account
```
✅ Instagram auto-connects (they're linked)

### LinkedIn Setup
```
1. Create LinkedIn App at linkedin.com/developers
2. Get App ID and Secret
3. Add to Settings → LinkedIn
4. Click "Connect"
5. Authorize with LinkedIn account
```
✅ Can now post to LinkedIn!

---

## 🎨 Architecture

```
Frontend (React + TypeScript + TailwindCSS)
    ↓
API Gateway (Flask REST API)
    ↓
Core Services:
  • YouTube API Service
  • Facebook Graph API Service
  • Instagram API Service
  • LinkedIn API Service
    ↓
Database (SQLite)
    ↓
Background Scheduler (APScheduler)
```

### Tech Stack
- **Backend**: Python, Flask
- **Frontend**: React, TypeScript, Vite
- **Database**: SQLite with WAL mode
- **Scheduling**: APScheduler
- **Styling**: TailwindCSS
- **APIs**: YouTube Data v3, Facebook Graph, LinkedIn OAuth

---

## 📚 Documentation

| Document                                             | Purpose                      |
| ---------------------------------------------------- | ---------------------------- |
| [HOW_TO_PUBLISH_SHORTS.md](HOW_TO_PUBLISH_SHORTS.md) | Complete guide to publishing |
| [QUICK_START.md](QUICK_START.md)                     | 5-minute setup guide         |
| [CONFIG_STATUS.md](CONFIG_STATUS.md)                 | Configuration details        |
| [OAUTH_LONG_TERM_SETUP.md](OAUTH_LONG_TERM_SETUP.md) | OAuth token setup            |

---

## 🔧 Advanced Configuration

### Automated Daily Publishing
Configure in **Settings → Automation**:
```json
{
  "enabled": true,
  "schedule_day": "monday",
  "youtube_schedule_time": "10:00",
  "social_media_schedule_time": "14:00",
  "auto_generate_captions": true
}
```

### Custom Caption Templates
Create templates in **Settings → Caption Templates**:
```
✨ Motivational: Inspiring message + emoji + CTA
📚 Educational: "Learn about X in 60 seconds"
🎯 Tutorial: "How to [action] - Quick tutorial"
```

### Optimal Posting Times
App learns from **Analytics** page:
- Tracks engagement by time of day
- Suggests best posting windows
- Auto-schedules to optimal times

---

## ⚡ Performance & Optimization

- **Fast Uploads**: Optimized video encoding
- **Parallel Publishing**: Publish to multiple channels simultaneously
- **Intelligent Retries**: Auto-retry failed publishes (3x)
- **Database Optimization**: SQLite WAL mode for concurrent access
- **Caching**: Smart caching of API responses
- **Background Jobs**: Non-blocking publishing

---

## 🐛 Troubleshooting

### Video Won't Upload
```
✓ Check file size (max 128MB)
✓ Verify audio codec (AAC or MP3)
✓ Ensure video is not corrupted
✓ Try different format (MP4 preferred)
```

### Publishing Failed
```
✓ Check internet connection
✓ Verify channel is still connected (Settings)
✓ Check YouTube upload quota (6/day limit)
✓ Retry: Select video → "Retry Publishing"
```

### Channels Not Showing
```
✓ Go to Settings
✓ Reconnect the platform
✓ Refresh page (F5)
✓ Clear browser cache
```

**More help:** See [HOW_TO_PUBLISH_SHORTS.md → Troubleshooting](HOW_TO_PUBLISH_SHORTS.md#-troubleshooting)

---

## 🎯 Pro Tips

1. **Post at Off-Peak Times** - Less competition, more visibility
2. **Repurpose Content** - Cut long videos into multiple shorts
3. **Use Caption Templates** - Save time, keep consistency
4. **Monitor Analytics** - Double down on what works
5. **Batch Schedule** - Schedule week's content in one go
6. **Test & Optimize** - Try different posting times/captions

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙋 Support & FAQ

### Q: Is this safe? Will my accounts be compromised?
**A:** Completely safe! We:
- Store tokens locally only (not in cloud)
- Never share credentials with third parties
- Use official OAuth 2.0 authentication
- No personal data is collected

### Q: Can I run this on a server/NAS?
**A:** Yes! The app supports:
- Docker deployment
- NAS hosting (Synology compatible)
- Linux servers
- Cloud platforms (AWS, Azure, etc.)

### Q: What's the upload limit?
**A:** 
- YouTube: 6 videos/day (platform limit)
- Facebook/Instagram: Unlimited
- LinkedIn: Unlimited

### Q: Can I schedule videos years in advance?
**A:** Yes! Schedule as far ahead as you want.

### Q: Does it work offline?
**A:** No, it needs internet to publish to platforms. But you can create content offline.

---

## 🚀 Roadmap

### v2.1 (Q2 2026)
- [ ] Per-channel custom scheduling
- [ ] Advanced caption templates with variables
- [ ] A/B testing for captions
- [ ] TikTok support

### v2.2 (Q3 2026)
- [ ] AI-powered optimal posting times
- [ ] Video editing within app
- [ ] Collaboration & team management
- [ ] Advanced analytics with predictions

### v3.0 (Q4 2026)
- [ ] Mobile app (iOS/Android)
- [ ] Live streaming support
- [ ] White-label solution
- [ ] Enterprise features

---

## 📞 Get in Touch

- 📧 **Email**: support@youtubeautomation.app
- 💬 **Discord**: [Join our community](https://discord.gg/youtubeautomation)
- 🐦 **Twitter**: [@YouTubeAutoApp](https://twitter.com/YouTubeAutoApp)
- 📖 **Docs**: [Full documentation](https://docs.youtubeautomation.app)

---

## 🙏 Acknowledgments

- Built with ❤️ for content creators
- Inspired by Buffer.com's simplicity
- Powered by open source libraries
- Special thanks to all contributors

---

**Ready to automate your video publishing?**

👉 **[Get Started Now](QUICK_START.md)**

---

*Last Updated: January 2026*  
*Version 2.0 - Cross-Channel Publishing Release*
