# Google Cloud OAuth Setup for YouTube Analytics API

## OAuth Client Configuration

When creating an OAuth 2.0 Client ID in Google Cloud Console, use these exact settings:

### Application Type
- **Web application**

### Name
- **Youtube-Scheduler** (or any name you prefer)

### Authorized JavaScript origins
Add these URLs (one per line):
```
http://localhost:5001
http://127.0.0.1:5001
```

**Important:** Use port 5001 (the default Flask port for this app). If you're running on a different port, use that port instead.

### Authorized redirect URIs
Add these URLs (one per line):
```
http://localhost:5001/oauth2callback
http://127.0.0.1:5001/oauth2callback
```

**Important:** 
- The OAuth callback URL is `/oauth2callback` (this is the standard Google OAuth callback path)
- The app is configured to use port 5001 for OAuth
- Make sure these URLs match exactly (including http vs https)

### For Production/Deployment
If deploying to a server with HTTPS, also add:
```
https://yourdomain.com/oauth2callback
https://yourdomain.com
```

## After Creating OAuth Client

1. **Download the JSON file:**
   - Click "Download JSON" or "Download" button
   - Save it as `client_secret.json`

2. **Place the file:**
   - Put `client_secret.json` in the project root directory
   - Same level as `run.py` and `app/` folder

3. **Restart the Flask server:**
   ```bash
   python run.py
   ```

4. **First-time authorization:**
   - When you first use YouTube API features, a browser window will open
   - Sign in with your Google account
   - Grant permissions
   - A `token.json` file will be created automatically

## Required APIs to Enable

Make sure these APIs are enabled in Google Cloud Console:
- ✅ **YouTube Data API v3** (for fetching videos/playlists)
- ✅ **YouTube Analytics API** (for analytics data)

## Troubleshooting

### "redirect_uri_mismatch" error
- Make sure the redirect URI in Google Cloud Console matches exactly: `http://localhost:5001/oauth2callback`
- Check that you're using port 5001 (check `run.py` or environment variable `PORT`)

### "Access blocked" error
- Make sure both APIs are enabled in Google Cloud Console
- Check that you're using the correct Google account

### Token not refreshing
- Delete `token.json` and re-authenticate
- Make sure `client_secret.json` is in the correct location
