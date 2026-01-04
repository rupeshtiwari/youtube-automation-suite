# Google OAuth Client Configuration Guide

## For YouTube Analytics API & YouTube Data API

When creating an OAuth 2.0 Client ID in Google Cloud Console (as shown in your screenshot), use these exact values:

---

## 📝 Configuration Values

### Application Type
- **Web application** ✅ (This is what you selected)

### Name
- **Youtube-Scheduler** (or any name you prefer)

---

## 🔗 Authorized JavaScript origins

**Purpose:** This is where your frontend application runs. Users initiate OAuth from here.

Add these URLs (one per line):
```
http://localhost:5001
http://127.0.0.1:5001
```

**Why:** Your Flask server runs on port 5001 and serves the React frontend. This is where OAuth requests originate.

---

## 🔄 Authorized redirect URIs

**Purpose:** This is where Google sends users back after they authorize your app.

Add these URLs (one per line):
```
http://localhost:5001/oauth2callback
http://127.0.0.1:5001/oauth2callback
```

**Why:** 
- The app uses Google's `InstalledAppFlow` which uses `/oauth2callback` as the standard callback path
- Port 5001 matches your Flask server port
- Both `localhost` and `127.0.0.1` are included for compatibility

---

## 🚀 For Production (When Deploying to NAS/Server)

If you deploy to a server with a domain, also add:

**Authorized JavaScript origins:**
```
https://your-domain.com
```

**Authorized redirect URIs:**
```
https://your-domain.com/oauth2callback
```

---

## ✅ After Configuration

1. Click **"Create"** button
2. Download the JSON file (click "Download JSON")
3. Save it as `client_secret.json` in your project root (same folder as `run.py`)
4. Restart your Flask server

---

## 📋 Quick Checklist

- [ ] Application type: **Web application**
- [ ] Name: **Youtube-Scheduler** (or your choice)
- [ ] Authorized JavaScript origins: `http://localhost:5001` and `http://127.0.0.1:5001`
- [ ] Authorized redirect URIs: `http://localhost:5001/oauth2callback` and `http://127.0.0.1:5001/oauth2callback`
- [ ] Click "Create"
- [ ] Download JSON file
- [ ] Save as `client_secret.json` in project root

---

## ⚠️ Important Notes

1. **Exact Match Required:** The redirect URI must match **exactly** (including `http://` vs `https://`, port number, and path)

2. **Port 5001:** This is your Flask server's default port. If you change it (via `PORT` environment variable), update these URIs accordingly.

3. **Multiple Environments:** You can add multiple URIs - one for local development, one for production, etc.

4. **API Enablement:** Make sure these APIs are enabled in Google Cloud Console:
   - ✅ YouTube Data API v3
   - ✅ YouTube Analytics API

---

## 🔧 Troubleshooting

### "redirect_uri_mismatch" error
- Verify the redirect URI in Google Cloud Console matches exactly: `http://localhost:5001/oauth2callback`
- Check your Flask server is running on port 5001
- Wait a few minutes after saving - changes can take time to propagate

### OAuth flow doesn't start
- Ensure `client_secret.json` is in the project root
- Check that both APIs (YouTube Data API v3 and YouTube Analytics API) are enabled
- Verify the file is valid JSON

---

## 📚 Reference

- Current Flask server port: **5001** (configured in `run.py`)
- OAuth callback path: **/oauth2callback** (standard Google OAuth path)
- Client secret file location: `client_secret.json` in project root

