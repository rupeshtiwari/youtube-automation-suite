# How to Get Facebook Page Access Token & Instagram Business Account ID

## 🔑 Step 1: Get New Facebook Page Access Token

### Method 1: Graph API Explorer (Easiest)

1. **Go to Graph API Explorer:**
   - https://developers.facebook.com/tools/explorer/

2. **Select Your App:**
   - In the top dropdown, select your app: `421181512329379`

3. **Add Permissions:**
   - Click "Add Permissions" or the permissions dropdown
   - Add these permissions:
     - `pages_manage_posts` (to post on Facebook Page)
     - `pages_read_engagement` (to read page data)
     - `instagram_basic` (to access Instagram data)
     - `instagram_content_publish` (to post on Instagram)
     - `business_management` (to manage business accounts)

4. **Generate Token:**
   - Click "Generate Access Token"
   - You may need to log in and authorize
   - Copy the token (it's a long string)

5. **Get Page Access Token:**
   - The token you get is a User Access Token
   - To get Page Access Token, make this API call:
   ```
   GET https://graph.facebook.com/v18.0/me/accounts?access_token={user-access-token}
   ```
   - Find your Page ID (`617021748762367`) in the response
   - Copy the `access_token` for that page

6. **Make Token Long-Lived (Optional but Recommended):**
   ```
   GET https://graph.facebook.com/v18.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id={app-id}&
     client_secret={app-secret}&
     fb_exchange_token={short-lived-token}
   ```

---

### Method 2: Using Facebook Page Settings

1. **Go to Your Facebook Page:**
   - https://www.facebook.com/pages/manage/

2. **Go to Settings:**
   - Click "Settings" in the left sidebar

3. **Go to Page Access:**
   - Click "Page Access" or "Page Roles"
   - You'll see access tokens there

---

## 📱 Step 2: Get Instagram Business Account ID

### Method 1: Using Graph API (Once You Have Valid Token)

Once you have a valid Facebook Page Access Token, run:

```bash
python3 scripts/get_instagram_account_id.py
```

This will automatically fetch your Instagram Business Account ID.

---

### Method 2: Manual Method (If Token Doesn't Work)

1. **Connect Instagram to Facebook Page:**
   - Go to your Facebook Page
   - Settings → Instagram
   - Connect your Instagram Business Account
   - **Important:** Your Instagram account must be a **Business Account** (not Personal)

2. **Get Instagram Account ID via Graph API Explorer:**
   - Go to: https://developers.facebook.com/tools/explorer/
   - Select your App
   - Use your Page Access Token
   - Make this API call:
     ```
     GET /{page-id}?fields=instagram_business_account
     ```
   - Replace `{page-id}` with: `617021748762367`
   - The response will have `instagram_business_account.id` - that's your Instagram Business Account ID

3. **Or Get from Page Settings:**
   - Facebook Page → Settings → Instagram
   - Your Instagram Business Account ID is shown there

---

## 🔐 Step 3: Get Facebook App Secret

1. **Go to Facebook Developers:**
   - https://developers.facebook.com/

2. **Select Your App:**
   - Click on your app: `421181512329379`

3. **Go to Settings:**
   - Click "Settings" → "Basic" in the left sidebar

4. **Find App Secret:**
   - Scroll down to "App Secret"
   - Click "Show" (you may need to verify your identity)
   - Copy the secret

---

## ✅ Quick Checklist

- [ ] Get new Facebook Page Access Token (Graph API Explorer)
- [ ] Get Facebook App Secret (Facebook Developers → Settings → Basic)
- [ ] Connect Instagram Business Account to Facebook Page
- [ ] Get Instagram Business Account ID (run script or manual method)
- [ ] Update `MY_CONFIG.json` with all credentials
- [ ] Load config: `python3 scripts/load_config.py`

---

## 🧪 Test Your Token

Once you have a new token, test it:

```bash
# Test if token works
curl "https://graph.facebook.com/v18.0/me?access_token={your-token}"

# Test if you can access your page
curl "https://graph.facebook.com/v18.0/617021748762367?access_token={your-token}"

# Test if Instagram account is connected
curl "https://graph.facebook.com/v18.0/617021748762367?fields=instagram_business_account&access_token={your-token}"
```

---

## 📝 Update MY_CONFIG.json

After getting all credentials, update `MY_CONFIG.json`:

```json
{
  "api_keys": {
    "facebook_app_secret": "YOUR_APP_SECRET",
    "facebook_page_access_token": "YOUR_NEW_PAGE_ACCESS_TOKEN",
    "instagram_business_account_id": "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID"
  }
}
```

Then load it:
```bash
python3 scripts/load_config.py
```

---

## 🚨 Common Issues

### "The access token could not be decrypted"
- Token is expired or invalid
- Get a new token from Graph API Explorer

### "No Instagram Business Account found"
- Instagram account is not connected to Facebook Page
- Instagram account is Personal (not Business)
- Connect Instagram Business Account in Facebook Page Settings

### "Insufficient permissions"
- Add required permissions in Graph API Explorer
- Make sure you're using Page Access Token (not User Access Token)

---

**Need help?** Check the error message and follow the troubleshooting steps above!

