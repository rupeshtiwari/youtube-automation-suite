# 🔑 Complete API Keys Setup Guide

This guide will walk you through obtaining all the API keys and access tokens needed for YouTube Automation.

## 📋 Table of Contents

1. [Google/YouTube API](#googleyoutube-api) ✅ Required
2. [LinkedIn API](#linkedin-api) - For LinkedIn posting
3. [Facebook API](#facebook-api) - For Facebook posting
4. [Instagram API](#instagram-api) - For Instagram posting
5. [Ayrshare API](#ayrshare-api) - Alternative unified API

---

## 1. Google/YouTube API ✅ Required

**Purpose:** Access YouTube data and schedule videos  
**Cost:** Free  
**Time:** 5-10 minutes

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown at the top
4. Click **"New Project"**
5. Enter project name: `YouTube Automation`
6. Click **"Create"**
7. Wait for project creation, then select it

### Step 2: Enable YouTube Data API v3

1. In the search bar at top, type: `YouTube Data API v3`
2. Click on **"YouTube Data API v3"**
3. Click **"Enable"** button
4. Wait for API to be enabled

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials** (left sidebar)
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**
4. If prompted, configure OAuth consent screen first:
   - User Type: **External** (or Internal if you have Workspace)
   - App name: `YouTube Automation`
   - User support email: Your email
   - Developer contact: Your email
   - Click **"Save and Continue"**
   - Scopes: Click **"Add or Remove Scopes"**
     - Search and add: `https://www.googleapis.com/auth/youtube.readonly`
     - Search and add: `https://www.googleapis.com/auth/youtube.force-ssl`
     - Click **"Update"** → **"Save and Continue"**
   - Test users: Add your email → **"Save and Continue"**
   - Click **"Back to Dashboard"**

5. Back to Credentials:
   - Application type: **"Desktop app"**
   - Name: `YouTube Automation Desktop`
   - Click **"Create"**

6. Download the credentials:
   - Click **"Download JSON"** button
   - Save the file as `client_secret.json`
   - **Important:** Place this file in your project directory

### Step 4: Verify Setup

The `client_secret.json` file should contain something like:
```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    ...
  }
}
```

**✅ Done!** The script will use this file for authentication.

---

## 2. LinkedIn API

**Purpose:** Post content to LinkedIn  
**Cost:** Free (Marketing Developer Platform access required)  
**Time:** 15-20 minutes

### Step 1: Create LinkedIn App

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Sign in with your LinkedIn account
3. Click **"Create app"** button
4. Fill in the form:
   - **App name:** `YouTube Automation`
   - **LinkedIn Page:** Select your company page (or create one)
   - **Privacy policy URL:** (You can use a placeholder like `https://yoursite.com/privacy`)
   - **App logo:** Optional
   - Accept terms and click **"Create app"**

### Step 2: Request Marketing Developer Platform Access

1. In your app dashboard, go to **"Products"** tab
2. Find **"Marketing Developer Platform"**
3. Click **"Request access"**
4. Fill out the form:
   - **Use case:** Select "Post organic content to LinkedIn"
   - **Company website:** Your website
   - **How do you plan to use the API?** Describe your automation
5. Submit and wait for approval (usually 1-2 business days)

### Step 3: Get Access Token

**Option A: Using LinkedIn's Token Generator (Easiest)**

1. Once approved, go to **"Auth"** tab in your app
2. Under **"OAuth 2.0 settings"**, note your:
   - **Client ID**
   - **Client Secret**
3. In **"Redirect URLs"**, add: `http://localhost:8080`
4. Click **"Generate a token"** button
5. Select scopes:
   - ✅ `w_member_social` (required for posting)
   - ✅ `r_liteprofile` or `r_basicprofile`
6. Click **"Generate token"**
7. **Copy the token** - this is your `LINKEDIN_ACCESS_TOKEN`

**Option B: Programmatic Access (Advanced)**

1. Follow OAuth 2.0 flow with these scopes:
   - `w_member_social`
   - `r_liteprofile`
2. Exchange authorization code for access token
3. Use refresh token to get new access tokens

### Step 4: Get Your Person URN

1. Go to [LinkedIn Profile](https://www.linkedin.com/me)
2. Check the URL - it will be like: `linkedin.com/in/yourname-123456/`
3. Or use LinkedIn API to get your URN:
   ```bash
   curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     https://api.linkedin.com/v2/me
   ```
4. Look for the `id` field - format: `urn:li:person:xxxxx`
5. This is your `LINKEDIN_PERSON_URN`

### Step 5: Configure in Web Interface

1. Open web interface: `http://localhost:5001`
2. Go to **Configuration** page
3. Enter:
   - **LinkedIn Access Token:** (from Step 3)
   - **LinkedIn Person URN:** `urn:li:person:xxxxx` (from Step 4)
4. Click **"Save Configuration"**

**✅ Done!** LinkedIn is configured.

---

## 3. Facebook API

**Purpose:** Post to Facebook Page  
**Cost:** Free  
**Time:** 10-15 minutes

### Step 1: Create Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Sign in with your Facebook account
3. Click **"My Apps"** → **"Create App"**
4. Select app type: **"Business"** or **"Other"**
5. Fill in:
   - **App name:** `YouTube Automation`
   - **App contact email:** Your email
   - Click **"Create App"**

### Step 2: Add Products

1. In your app dashboard, find **"Add Products"**
2. Click **"Set Up"** for:
   - ✅ **Facebook Login** (required for authentication)
   - ✅ **Pages** (required for posting to pages)

### Step 3: Configure Facebook Login

1. Go to **Facebook Login** → **Settings**
2. Add **Valid OAuth Redirect URIs:**
   - `http://localhost:8080`
   - `https://localhost:8080`
3. Click **"Save Changes"**

### Step 4: Get Page Access Token

**Method 1: Graph API Explorer (Easiest)**

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from **"Meta App"** dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   - ✅ `pages_show_list`
   - ✅ `pages_read_engagement`
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_user_content`
5. Click **"Generate Access Token"**
6. Copy this token temporarily

**Get Long-Lived Token:**

1. In Graph API Explorer, make this call:
   ```
   GET /oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN
   ```
2. Replace:
   - `YOUR_APP_ID`: From App Dashboard → Settings → Basic
   - `YOUR_APP_SECRET`: From App Dashboard → Settings → Basic (click "Show")
   - `SHORT_LIVED_TOKEN`: The token from step above
3. The response contains `access_token` - this is your long-lived token

**Get Page Access Token:**

1. In Graph API Explorer, with your token, call:
   ```
   GET /me/accounts
   ```
2. This returns your pages with `access_token` for each
3. Copy the `access_token` for your target page - this is your `FACEBOOK_PAGE_ACCESS_TOKEN`

### Step 5: Get Page ID

1. Go to your Facebook Page
2. Click **"About"** on the left sidebar
3. Scroll down to find **"Page ID"**
4. Or use Graph API:
   ```
   GET /me/accounts
   ```
   The `id` field is your `FACEBOOK_PAGE_ID`

### Step 6: Configure in Web Interface

1. Open web interface: `http://localhost:5001`
2. Go to **Configuration** page
3. Enter:
   - **Facebook Page Access Token:** (from Step 4)
   - **Facebook Page ID:** (from Step 5)
4. Click **"Save Configuration"**

**✅ Done!** Facebook is configured.

---

## 4. Instagram API

**Purpose:** Post to Instagram Business Account  
**Cost:** Free  
**Time:** 15-20 minutes  
**Note:** Requires Facebook Page connected to Instagram Business Account

### Step 1: Convert to Business Account

1. Open Instagram app on your phone
2. Go to **Settings** → **Account** → **Switch to Professional Account**
3. Choose **"Business"**
4. Connect to your Facebook Page (created in Facebook setup)
5. Complete the setup

### Step 2: Link Instagram to Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your app (from Facebook setup)
3. Go to **"Add Products"**
4. Click **"Set Up"** for **"Instagram Graph API"**

### Step 3: Get Instagram Business Account ID

**Method 1: Using Graph API Explorer**

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Use your Facebook Page Access Token
4. Call:
   ```
   GET /{page-id}?fields=instagram_business_account
   ```
   Replace `{page-id}` with your Facebook Page ID
5. Response contains `instagram_business_account.id` - this is your `INSTAGRAM_BUSINESS_ACCOUNT_ID`

**Method 2: Using Facebook Graph API**

```bash
curl -X GET "https://graph.facebook.com/v18.0/{page-id}?fields=instagram_business_account&access_token={page-access-token}"
```

### Step 4: Get Instagram Access Token

**Instagram uses the same access token as Facebook Page!**

Your `INSTAGRAM_ACCESS_TOKEN` is the same as your `FACEBOOK_PAGE_ACCESS_TOKEN` from the Facebook setup.

### Step 5: Verify Instagram Access

Test with Graph API:
```bash
curl -X GET "https://graph.facebook.com/v18.0/{instagram-business-account-id}?fields=username,profile_picture_url&access_token={page-access-token}"
```

### Step 6: Configure in Web Interface

1. Open web interface: `http://localhost:5001`
2. Go to **Configuration** page
3. Enter:
   - **Instagram Business Account ID:** (from Step 3)
   - **Instagram Access Token:** (same as Facebook Page Access Token)
4. Click **"Save Configuration"**

**✅ Done!** Instagram is configured.

**Important Notes:**
- Instagram API requires images for posts
- Use Ayrshare for easier Instagram posting (handles images automatically)
- Native Instagram API is more complex

---

## 5. Ayrshare API (Alternative - Recommended)

**Purpose:** Unified API for all social platforms  
**Cost:** Free tier available, paid plans for production  
**Time:** 5 minutes  
**Why use it:** Much simpler than native APIs, handles Instagram images automatically

### Step 1: Sign Up

1. Go to [Ayrshare](https://www.ayrshare.com/)
2. Click **"Get Started"** or **"Sign Up"**
3. Create account with your email
4. Verify your email

### Step 2: Connect Social Media Accounts

1. After login, go to **Dashboard**
2. Click **"Connect Accounts"** or **"Social Profiles"**
3. Connect:
   - ✅ LinkedIn
   - ✅ Facebook Page
   - ✅ Instagram Business Account
4. Authorize each platform (OAuth flow)

### Step 3: Get API Key

1. Go to **Dashboard** → **API Key** or **Settings**
2. Your API key is displayed
3. Click **"Copy"** or **"Show API Key"**
4. This is your `AYRSHARE_API_KEY`

### Step 4: Configure in Web Interface

1. Open web interface: `http://localhost:5001`
2. Go to **Configuration** page
3. Enter:
   - **Ayrshare API Key:** (from Step 3)
4. Click **"Save Configuration"**
5. **Enable "Use Ayrshare"** in the posting options

**✅ Done!** Ayrshare is configured.

**Benefits:**
- ✅ One API key for all platforms
- ✅ Handles Instagram images automatically
- ✅ Simpler authentication
- ✅ Better error handling

---

## 📝 Quick Reference: Where to Find Each Key

| Service | What You Need | Where to Find |
|---------|---------------|---------------|
| **YouTube** | `client_secret.json` | Google Cloud Console → Credentials → Download JSON |
| **LinkedIn** | Access Token + Person URN | LinkedIn Developers → Auth → Generate Token |
| **Facebook** | Page Access Token + Page ID | Facebook Developers → Graph API Explorer |
| **Instagram** | Business Account ID + Access Token | Facebook Graph API (same token as Facebook) |
| **Ayrshare** | API Key | Ayrshare Dashboard → API Key |

---

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   - All keys are in `.env` file (already in `.gitignore`)
   - Web interface stores in `automation_settings.json` (also in `.gitignore`)

2. **Rotate keys regularly**
   - LinkedIn tokens expire (use refresh tokens)
   - Facebook tokens can be revoked
   - Update keys if compromised

3. **Use environment variables**
   - Keys are stored securely
   - Never share keys publicly

4. **Test in development first**
   - Use test/sandbox accounts if available
   - Verify posting works before production

---

## ✅ Configuration Checklist

After setting up all APIs, verify:

- [ ] Google OAuth: `client_secret.json` file in project directory
- [ ] LinkedIn: Access Token + Person URN configured
- [ ] Facebook: Page Access Token + Page ID configured
- [ ] Instagram: Business Account ID + Access Token configured (or use Ayrshare)
- [ ] Ayrshare: API Key configured (optional but recommended)
- [ ] All keys saved in web interface Configuration page
- [ ] Test connections using "Test Connections" button

---

## 🆘 Troubleshooting

### "Invalid Access Token"
- Token may have expired
- Generate a new token
- For LinkedIn: Use refresh token flow

### "Insufficient Permissions"
- Check that you've added required scopes/permissions
- Re-authorize the app
- For Facebook: Make sure Pages product is added

### "Page Not Found" (Facebook/Instagram)
- Verify Page ID is correct
- Ensure Instagram is connected to Facebook Page
- Check that Page Access Token has correct permissions

### "API Rate Limit Exceeded"
- Wait before retrying
- Reduce posting frequency
- Consider upgrading API plan

---

## 📚 Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api)
- [Ayrshare API Documentation](https://docs.ayrshare.com/)

---

**Need help?** Check the web interface Configuration page for connection testing tools!

