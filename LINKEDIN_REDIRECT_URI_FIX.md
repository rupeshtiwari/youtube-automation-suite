# LinkedIn Redirect URI Fix

## 🔴 Error: "The redirect_uri does not match the registered value"

This error occurs when the redirect URI used in the OAuth flow doesn't exactly match what's registered in your LinkedIn app settings.

## ✅ Solution

### Step 1: Find Your Redirect URI

The redirect URI your app uses is:
```
http://localhost:5001/api/linkedin/oauth/callback
```

**OR** (if using a different host/port):
```
http://127.0.0.1:5001/api/linkedin/oauth/callback
```

### Step 2: Add to LinkedIn App Settings

1. Go to: https://www.linkedin.com/developers/apps
2. Click on your app: **FullStack Master** (Client ID: `86vimp2gbw3c06`)
3. Go to **"Auth"** tab (or "OAuth 2.0 settings")
4. Under **"Authorized redirect URLs for your app"**, click **"Add redirect URL"**
5. Add **EXACTLY** this URL:
   ```
   http://localhost:5001/api/linkedin/oauth/callback
   ```
6. Click **"Update"** or **"Save"**

### Step 3: Important Notes

- The redirect URI must match **EXACTLY** (including `http://` vs `https://`, `localhost` vs `127.0.0.1`, port number, and path)
- If you're running on a different port, update both:
  - The redirect URI in LinkedIn app settings
  - The port in your Flask app (currently 5001)
- For production, you'll need to add your production URL too

### Step 4: Test Again

After adding the redirect URI:
1. Go to: http://localhost:5001/config
2. Click "Connect LinkedIn & Fetch All Details"
3. It should work now!

## 🔍 How to Check Current Redirect URI

When you click the Connect button, a flash message will show the exact redirect URI being used. Make sure that EXACT value is registered in LinkedIn.

## 📝 Multiple Redirect URIs

You can add multiple redirect URIs in LinkedIn:
- `http://localhost:5001/api/linkedin/oauth/callback` (for local development)
- `https://yourdomain.com/api/linkedin/oauth/callback` (for production)

Just make sure the one being used matches exactly!

