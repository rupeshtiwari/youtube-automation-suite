# 🔐 Add Facebook App Secret - Quick Guide

Your Facebook one-click login button is almost ready! You just need to add your **Facebook App Secret** in one minute.

## Step 1: Get Your Facebook App Secret

1. Go to: https://developers.facebook.com/apps/421181512329379/settings/basic
2. Find the **App Secret** section
3. Click **"Show"** to reveal it
4. **Copy** the entire secret (it's a long string of characters)

## Step 2: Add to Your System

### Option A: Edit `.env` File (Recommended)

1. Open: `/Users/rupesh/code/youtube-automation/.env`
2. Find or add this line:
   ```
   FACEBOOK_APP_SECRET=your_secret_here
   ```
3. Replace `your_secret_here` with your actual secret
4. Save the file

**Example:**
```
FACEBOOK_APP_ID=421181512329379
FACEBOOK_APP_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

## Step 3: Restart the Server

In Terminal:
```bash
# Kill old server
lsof -i :5001 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Start new server
/Users/rupesh/code/youtube-automation/.venv/bin/python /Users/rupesh/code/youtube-automation/run.py
```

Or if you're using a start script:
```bash
./QUICK_RESTART.sh
```

## Step 4: Test It!

1. Refresh the app in your browser (Cmd+Shift+R to hard refresh)
2. Go to Settings → Platform Connections
3. Click "Connect" on Facebook/Instagram
4. You'll now be able to login with Meta! 🎉

---

## What's the Facebook App Secret?

The **App Secret** is like a password for your Facebook app. It allows the server to:
- Securely exchange your login code for tokens
- Prove to Facebook that the request is coming from your app
- Fetch your Page ID and Instagram Business Account ID automatically

Think of it like a house key - without it, you can't open the door!

## Troubleshooting

### "Still showing secret required message"
- Make sure you restarted the server after adding the secret
- Check that the `.env` file was saved correctly
- Hard refresh the browser (Cmd+Shift+R)

### Can't find the App Secret
- Make sure you're logged into the right Facebook developer account
- The App Secret should be on the "Settings → Basic" page
- Don't confuse it with Client Secret (different thing)

### Getting an error during login
- Check that your Facebook App is in **Development** or **Live** mode (not disabled)
- Make sure the redirect URL matches what you set in Facebook Developer Console

---

**Once added, your one-click Facebook/Instagram login will work perfectly!** 🚀
