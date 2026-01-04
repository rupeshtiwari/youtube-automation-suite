# 🔗 LinkedIn OAuth Setup Guide

## ⚠️ If you see "Bummer, something went wrong" error

**Error:** "The redirect_uri does not match the registered value"

This happens when LinkedIn's registered redirect URI doesn't match what the app is sending.

---

## ✅ How to Fix

### Step 1: Get Your LinkedIn App ID
1. Go to https://www.linkedin.com/developers/apps
2. Select or create your app
3. Copy your **Client ID**

### Step 2: Register Redirect URI in LinkedIn Settings
1. In your LinkedIn App settings
2. Go to **"Authorized redirect URLs for your app"**
3. Add this exact URL:
   ```
   http://127.0.0.1:5001/api/linkedin/oauth/callback
   ```
   
**⚠️ CRITICAL:** Must be exactly:
- `http://` (not https)
- `127.0.0.1` (not localhost)
- `:5001` (with port)
- `/api/linkedin/oauth/callback` (exact path)

### Step 3: Add to Settings
1. Open the app at http://127.0.0.1:5001
2. Go to **Settings** ⚙️
3. Scroll to **LinkedIn** section
4. Click **"Connect"**
5. Verify LinkedIn Client ID & Secret are configured
6. LinkedIn OAuth will now work!

---

## 📋 Checklist

- [ ] LinkedIn app created at developers.linkedin.com
- [ ] Client ID copied
- [ ] Client Secret copied
- [ ] Redirect URI set to: `http://127.0.0.1:5001/api/linkedin/oauth/callback`
- [ ] App settings show "LinkedIn: Configured"
- [ ] Clicked "Connect" and authorized

---

## 🆘 Still Getting Error?

**Check:**
1. Redirect URI is EXACTLY as shown above (case-sensitive)
2. Using `127.0.0.1` not `localhost`
3. Port is `:5001`
4. Full path is `/api/linkedin/oauth/callback`
5. LinkedIn app doesn't have product limitations

**If still failing:**
1. Delete cookies for 127.0.0.1:5001
2. Hard refresh page (Cmd+Shift+R or Ctrl+Shift+R)
3. Try again

---

## ✨ Success!

Once you see "LinkedIn: Connected" ✅ in Settings, you can:
- Publish shorts to LinkedIn
- Share content on your profile
- Access LinkedIn insights

Enjoy! 🚀
