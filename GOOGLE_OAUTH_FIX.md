# ✅ Google OAuth Configuration - CORRECT SETUP

## ⚠️ Problem
Google OAuth **does NOT accept `.local` domains** like `youtube-automation.local`. You'll get this error:
```
Invalid redirect: Must end with a public top-level domain (such as .com or .org).
```

## ✅ Solution: Use `localhost` for Local Development

### In Google Cloud Console OAuth Client Configuration:

**Application type:** Web application

**Authorized JavaScript origins:**
```
http://localhost:5001
http://127.0.0.1:5001
```

**Authorized redirect URIs:**
```
http://localhost:5001/oauth2callback
http://127.0.0.1:5001/oauth2callback
```

### Steps:
1. Remove the `.local` URI from the redirect URIs field
2. Add the `localhost` URIs above
3. Click **"Save"** or **"Create"**
4. Wait 1-2 minutes for changes to propagate

## 📝 Why This Works

- Google OAuth accepts `localhost` and `127.0.0.1` for local development
- Your Flask app runs on port 5001
- The OAuth callback path is `/oauth2callback` (standard Google path)
- The code uses `run_local_server(port=5001)` which automatically uses `localhost`

## 🔄 After Configuration

1. Download the updated `client_secret.json` (if you created a new client)
2. Save it in your project root (same folder as `run.py`)
3. Restart your Flask server
4. Try OAuth authentication again

## 🚀 For Production (Later)

When you deploy to a server with a real domain, add:
- **Authorized JavaScript origins:** `https://your-domain.com`
- **Authorized redirect URIs:** `https://your-domain.com/oauth2callback`

You can have multiple URIs configured - one for local dev, one for production.

## ✅ Quick Checklist

- [ ] Removed `.local` domain from redirect URIs
- [ ] Added `http://localhost:5001/oauth2callback`
- [ ] Added `http://127.0.0.1:5001/oauth2callback` (optional but recommended)
- [ ] Saved changes in Google Cloud Console
- [ ] Updated `client_secret.json` if needed
- [ ] Restarted Flask server

---

**Note:** The `.local` domain setup is still useful for accessing your app at `http://youtube-automation.local:5001` via `/etc/hosts`, but OAuth must use `localhost` in the Google Cloud Console configuration.

