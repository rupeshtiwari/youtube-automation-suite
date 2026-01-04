# 🚀 Getting Started - YouTube Automation Suite

**Complete setup in 5 minutes!**

---

## Step 1: Install & Start (2 minutes)

### Prerequisites
- Python 3.8 or higher: [Download Python](https://www.python.org/)
- Git (optional): [Download Git](https://git-scm.com/)

### Installation

```bash
# 1. Navigate to project directory
cd youtube-automation

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate it
# On Mac/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# 4. Install packages
pip install -r requirements.txt

# 5. Start the app
python run.py
```

✅ **App is now running at:** http://localhost:5001

---

## Step 2: First-Time Setup (3 minutes)

### 1. Open Settings
Click ⚙️ **Settings** in the left sidebar

### 2. Connect YouTube (Essential)
**Button:** Click "Connect" next to YouTube

```
↓ Browser opens Google login
↓ Click "Allow" to authorize
↓ You're redirected back to Settings
✅ Shows: "✅ Ready" (green status)
```

### 3. Connect Facebook/Instagram (Optional but Recommended)
**Button:** Click "Connect" next to Facebook

```
↓ Pop-up opens Facebook login
↓ Click "Continue"  
↓ App gets access to your pages
✅ Instagram auto-connects (linked to Facebook)
```

### 4. Connect LinkedIn (Optional)
**Button:** Click "Connect" next to LinkedIn

```
↓ Pop-up opens LinkedIn login
↓ Click "Allow" 
✅ Shows: "✅ Connected" (green status)
```

### Done! 🎉
All platforms now show green ✅ status

---

## Step 3: Publish Your First Short

### Upload a Video
```
1. Click "🎬 Shorts" in sidebar
2. Click "📤 Upload Video"
3. Select a short video file (MP4, WebM, etc.)
4. Must be ≤60 seconds
5. Click "Save"
```

### Generate Caption
```
1. Your video appears in library
2. Click "✨ Generate Caption"
3. App creates engaging caption
4. Edit if you want
5. Click "Save"
```

### Publish to Multiple Channels
```
1. Click "📅 Queue" (home page)
2. Find your video
3. Click "➕" button (Publish to Channels)
4. Select channels:
   ✓ YouTube
   ✓ Facebook  
   ✓ Instagram
   ✓ LinkedIn
5. Pick date & time
6. Click "Schedule Publishing"
```

### ✨ You're Done!
Your short automatically publishes to all channels!

---

## 📍 Where Everything Is

| What                    | Location                      | Icon |
| ----------------------- | ----------------------------- | ---- |
| **Publishing Queue**    | Home page                     | 📅    |
| **Upload Videos**       | Shorts → Upload               | 🎬    |
| **Schedule Calendar**   | Calendar → View all scheduled | 🗓️    |
| **Analytics**           | Analytics page                | 📊    |
| **Settings & Channels** | Settings                      | ⚙️    |

---

## 🎯 Common Tasks

### Task: Schedule a video for tomorrow at 10 AM
```
1. Queue → Your Video → ➕
2. Select channels
3. Set date: Tomorrow
4. Set time: 10:00 AM
5. Click Schedule
```

### Task: Publish to YouTube only (not Facebook)
```
1. Queue → Your Video → ➕
2. Select ONLY YouTube ✓
3. Uncheck Facebook, Instagram, LinkedIn
4. Pick time
5. Schedule
```

### Task: View when my post was published
```
1. Queue → Your Video
2. Status shows: Published ✓
3. Time shows: "Published at 10:00 AM"
```

### Task: See how many views/likes each post got
```
1. Analytics → View all videos
2. Shows views, likes, shares
3. Per-platform breakdown
4. Click video for detailed stats
```

---

## ⚡ Pro Tips for Power Users

### Tip 1: Batch Upload
Upload 5 videos at once:
```
Shorts → Upload Video (repeat 5 times)
All added to library
```

### Tip 2: Quick Scheduling
Schedule entire week in one session:
```
Queue → Select Video 1 → Schedule (Mon 10 AM)
Queue → Select Video 2 → Schedule (Tue 10 AM)
Queue → Select Video 3 → Schedule (Wed 10 AM)
... etc
```

### Tip 3: Repurpose Content
One long video → Multiple shorts:
```
1. Upload long video (30 min)
2. Sessions → Split into 60-sec clips
3. Each clip becomes separate short
4. Schedule all clips to same channels
5. Auto-publishes throughout week
```

### Tip 4: Use Caption Templates
Set your style once, use forever:
```
Settings → Caption Templates
Create: "Motivational" template
Create: "Educational" template
Create: "Tutorial" template

Then use templates when generating captions!
```

### Tip 5: Optimal Times
Post when your audience is most active:
```
Analytics → See "Best Times to Post"
Schedule your videos for those times
Monitor results
Adjust based on engagement
```

---

## 🆘 Quick Fixes

### Problem: "Channels not showing"
**Fix:** 
1. Go to Settings
2. Click Reconnect for that platform
3. Refresh page (F5)

### Problem: "Upload failed"
**Fix:**
1. Check file size (max 128 MB)
2. Verify it's a video file (MP4, WebM, MOV)
3. Check file isn't corrupted
4. Try again

### Problem: "Upload too slow"
**Fix:**
1. Check internet connection speed
2. Compress video: Use HandBrake
3. Reduce resolution: 1080p instead of 4K
4. Try again

### Problem: "App won't start"
**Fix:**
```bash
# Kill old process
kill $(lsof -i :5001 | grep -v COMMAND | awk '{print $2}')

# Start fresh
python run.py
```

### Problem: "Port 5001 already in use"
**Fix:**
```bash
# See what's using port
lsof -i :5001

# Kill the process
kill -9 [PID]

# Try again
python run.py
```

---

## 🎓 What You Can Do Now

✅ **Upload shorts** from your computer  
✅ **Generate captions** automatically  
✅ **Publish to YouTube** directly  
✅ **Cross-post to Facebook** in one click  
✅ **Auto-publish to Instagram** too  
✅ **Share on LinkedIn** as video link  
✅ **Schedule everything** in advance  
✅ **Track analytics** for all platforms  
✅ **Automate posting** on a schedule  

---

## 📚 Next Steps

Now that you're set up:

1. **Learn More**: Read [HOW_TO_PUBLISH_SHORTS.md](HOW_TO_PUBLISH_SHORTS.md)
2. **Deep Dive**: Check [README_MAIN.md](README_MAIN.md) for all features
3. **Troubleshoot**: See [HOW_TO_PUBLISH_SHORTS.md#-troubleshooting](HOW_TO_PUBLISH_SHORTS.md#-troubleshooting)

---

## 🎉 You're All Set!

Your YouTube Automation Suite is ready to use.

**Start by:**
1. Upload a short video
2. Generate a caption
3. Publish to your channels

**Questions?** Check the [FAQ section](HOW_TO_PUBLISH_SHORTS.md#-faq) or [Troubleshooting](HOW_TO_PUBLISH_SHORTS.md#-troubleshooting) guide.

---

*Happy creating!* 🚀

**Last Updated: January 2026**  
**Version: 2.0**
