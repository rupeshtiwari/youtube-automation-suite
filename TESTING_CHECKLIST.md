# Testing Checklist - Critical Features

## 📋 What I Need From You

### Step 1: Fill in MY_CONFIG.json
1. Open `MY_CONFIG.json` in the editor
2. Fill in your API credentials:
   - LinkedIn Client ID & Secret
   - Facebook App ID & Secret
   - Instagram Business Account ID
   - Any access tokens you have
   - Your social media URLs
   - WhatsApp number
3. Save the file
4. Tell me "Config ready"

### Step 2: I'll Load It
- I'll load your config into the database
- Settings will appear in the Config page
- You can verify everything is correct

### Step 3: Testing Critical Features

#### Test 1: Native Video Upload (LinkedIn)
**What I need:**
- A test YouTube video URL (short video, < 5 minutes)
- Or I can use one of your existing videos

**What we'll test:**
1. Download video from YouTube
2. Upload natively to LinkedIn
3. Create post with caption
4. Verify it's published

**Expected result:** Video appears on LinkedIn as native video (not link)

---

#### Test 2: Native Video Upload (Facebook)
**What I need:**
- Same test video or different one

**What we'll test:**
1. Download video from YouTube
2. Upload natively to Facebook Page
3. Create post with caption
4. Verify it's published

**Expected result:** Video appears on Facebook Page as native video

---

#### Test 3: Native Video Upload (Instagram)
**What I need:**
- Same test video (Instagram Reels format)

**What we'll test:**
1. Download video from YouTube
2. Upload as Instagram Reel
3. Create post with caption
4. Verify it's published

**Expected result:** Video appears on Instagram as Reel

---

#### Test 4: Auto-Publishing Scheduler
**What I need:**
- Nothing - I'll schedule a test post

**What we'll test:**
1. Schedule a post for 2 minutes in the future
2. Wait for auto-publisher to trigger (runs every 15 min)
3. Check Activity logs
4. Verify post was published automatically

**Expected result:** Post is automatically published at scheduled time

---

## 🎯 Quick Start

### Option 1: Load Config via Web UI
1. Fill in `MY_CONFIG.json`
2. Go to Config page
3. Click "Load from MY_CONFIG.json" button
4. Settings will be loaded

### Option 2: Load Config via Command Line
```bash
python scripts/load_config.py
```

---

## ⚠️ Important Notes

1. **API Credentials**: Make sure all credentials are valid and have proper permissions
2. **Test Videos**: Use short videos (< 5 min) for faster testing
3. **Permissions**: Ensure your API tokens have:
   - LinkedIn: `w_member_social` permission
   - Facebook: `pages_manage_posts` permission
   - Instagram: `instagram_basic`, `instagram_content_publish` permissions

---

## 📝 What to Provide

**Minimum Required:**
- LinkedIn Client ID & Secret
- Facebook App ID & Secret
- Facebook Page ID
- Instagram Business Account ID
- At least one test YouTube video URL

**Optional but Recommended:**
- LinkedIn Access Token (if you have one)
- Facebook Page Access Token (if you have one)
- Instagram Access Token (if you have one)
- All social media URLs
- WhatsApp number

---

## ✅ After You Provide Config

Once you fill in `MY_CONFIG.json` and tell me "Config ready", I will:

1. ✅ Load your config into the database
2. ✅ Verify all settings are saved
3. ✅ Test each platform's native video upload
4. ✅ Test auto-publishing scheduler
5. ✅ Report results and fix any issues

---

## 🚨 If Something Fails

If a test fails, I'll:
- Show you the exact error
- Fix the code if needed
- Retry the test
- Document what works and what doesn't

---

**Ready? Fill in `MY_CONFIG.json` and tell me when you're done!** 🚀

