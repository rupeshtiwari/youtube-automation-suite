# 🚀 Facebook One-Click Setup Guide

## Current Status

Your app already has a Facebook App ID configured: `421181512329379`

To enable **one-click automatic token fetching**, you need to add your **Facebook App Secret**.

## How to Get Facebook App Secret

### Step 1: Open Facebook Developer Console
Go to: https://developers.facebook.com/apps

### Step 2: Select Your App
Click on your app (YouTube Automation App ID: 421181512329379)

### Step 3: Find Settings → Basic
- Left sidebar → Settings → Basic
- You'll see your App ID and **App Secret**
- Click "Show" next to App Secret to reveal it

### Step 4: Copy the App Secret
Copy the complete string (it looks like: `7f1a2b3c4d5e6f7g8h9i0j...`)

### Step 5: Add to Environment

#### Option A: Update .env file
Open `/Users/rupesh/code/youtube-automation/.env` and add:
```
FACEBOOK_APP_SECRET=your_app_secret_here
```

#### Option B: Update via Settings (Coming Soon)
Admin panel will allow setting this via UI.

### Step 6: Restart the Server
```bash
kill $(lsof -i :5001 | grep -v COMMAND | awk '{print $2}')
/Users/rupesh/code/youtube-automation/.venv/bin/python /Users/rupesh/code/youtube-automation/run.py
```

### Step 7: Test One-Click Setup
1. Go to Settings page
2. Click "🤖 Login with Meta" button
3. Login to your Facebook account
4. System will automatically:
   - ✓ Fetch your Facebook Page Access Token
   - ✓ Get your Page ID
   - ✓ Get your Instagram Business Account ID (if linked)
   - ✓ Save everything to the database
5. You'll be redirected back to Settings with everything configured!

## What Happens Behind the Scenes

```
1. User clicks "Login with Meta"
   ↓
2. Redirects to Facebook OAuth consent screen
   ↓
3. User logs in and grants permission
   ↓
4. Facebook redirects back with auth code
   ↓
5. App exchanges code for user token
   ↓
6. App fetches all Pages associated with user
   ↓
7. App gets Page Access Token (doesn't expire like user token)
   ↓
8. App gets Instagram Business Account ID (if linked)
   ↓
9. Everything saved to database automatically ✅
   ↓
10. User redirected back to Settings - DONE!
```

## Fallback: Manual Method Still Available

If you don't want to set up the Facebook App Secret, you can still:
1. Use "📋 Manual Token Entry" on Settings page
2. Or click "📖 Step-by-Step Guide" to get tokens from Facebook Graph Explorer
3. Paste them manually

But **one-click setup is much faster!** ⚡

## Troubleshooting

### "Facebook Login Failed"
- Check that your Facebook App is not in Development mode
- Verify the App ID is correct
- Make sure you're using a verified Business Account

### "No Pages Found"
- Your Facebook user account must have admin access to at least one Facebook Page
- Create a Page first if you don't have one

### "Instagram account not linked"
- Not all Pages have Instagram Business Accounts
- This is optional - the system will work fine without it

## Need Help?

Check your Facebook App Dashboard:
https://developers.facebook.com/apps/421181512329379

---

**Next Step:** Get your App Secret and add it to `.env`, then restart the server!
