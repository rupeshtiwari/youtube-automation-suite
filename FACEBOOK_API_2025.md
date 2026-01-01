# Facebook API 2025 - Latest Updates & Methods

## 🚨 Important Changes (2025)

### 1. All Videos Are Now Reels
- **As of June 2025**, Facebook has transitioned ALL video content to Reels format
- Any video uploaded, regardless of length, is now classified as a Reel
- You must use the **Reels API** for video uploads

### 2. Facebook Login OAuth Issues
- Many apps are seeing "Facebook Login is currently unavailable for this app"
- This is due to:
  - App not properly configured in Facebook Developer Dashboard
  - App needs to be in production mode (not just development)
  - Missing required app details (Privacy Policy, etc.)
  - App review may be required for certain permissions

## ✅ Recommended Method: Graph API Explorer

**The most reliable way to get tokens in 2025:**

### Step 1: Use Graph API Explorer
1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your App in the dropdown
3. Click "Get Token" → "Get User Access Token"
4. Select required permissions
5. Generate token
6. Copy the token

### Step 2: Get Page Access Token
Use the script:
```bash
python3 scripts/get_facebook_token_v2.py
```

Or manually:
1. Visit: `https://graph.facebook.com/v18.0/me/accounts?access_token={your-token}`
2. Find your Page ID
3. Copy the `access_token` for that page

## 📋 Required Permissions

For video publishing, you need:
- `pages_manage_posts` - Publish posts to pages
- `pages_read_engagement` - Read page data
- `pages_show_list` - List user's pages
- `instagram_basic` - Access Instagram data
- `instagram_content_publish` - Publish to Instagram
- `business_management` - Manage business accounts

## 🔧 Fix "Facebook Login Unavailable" Error

### Option 1: Configure App Properly
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your App
3. **Settings → Basic:**
   - Fill all required fields
   - Add Privacy Policy URL
   - Add App Domains
   - Save changes

4. **Products → Facebook Login:**
   - Enable Facebook Login
   - Add Valid OAuth Redirect URIs
   - Enable "Client OAuth Login"
   - Enable "Web OAuth Login"
   - Save changes

5. **App Review:**
   - Submit app for review if needed
   - Request Advanced Access for permissions

### Option 2: Use Graph API Explorer (Easier)
- Skip OAuth entirely
- Use Graph API Explorer to get tokens
- More reliable, no app configuration needed

## 📹 Publishing Videos (Reels API)

### Facebook Reels API
```python
# Upload video as Reel
POST /{page-id}/video_reels
{
    "video_file": <file>,
    "description": "Your caption",
    "access_token": "<page-access-token>"
}
```

### Instagram Reels API
```python
# Step 1: Create container
POST /{ig-business-account-id}/media
{
    "media_type": "REELS",
    "video_file": <file>,
    "caption": "Your caption",
    "access_token": "<access-token>"
}

# Step 2: Publish
POST /{ig-business-account-id}/media_publish
{
    "creation_id": "<container-id>",
    "access_token": "<access-token>"
}
```

## 🚀 Quick Start

1. **Get Token:**
   ```bash
   python3 scripts/get_facebook_token_v2.py
   ```

2. **Test Upload:**
   - Use the updated video processor
   - It now uses Reels API automatically

## 📚 Resources

- [Facebook Reels API Docs](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Facebook Developer Dashboard](https://developers.facebook.com/)

---

**Note:** The OAuth flow may not work if your app isn't fully configured. Use Graph API Explorer method instead - it's more reliable!

