# Instagram Setup Guide for Video Posting

## ⚠️ Important: You Need Instagram Graph API (Not Basic Display)

The documentation you shared is for **Instagram Basic Display API** (for reading user data). 

For **posting videos/content**, you need **Instagram Graph API** which uses **Facebook Login**.

---

## 📋 What You Need for Instagram Video Posting

### Required Credentials:

1. **Facebook App ID** ✅ (You have: `421181512329379`)
2. **Facebook App Secret** ❌ (You need this)
3. **Facebook Page ID** ✅ (You have: `617021748762367`)
4. **Facebook Page Access Token** ✅ (You have one)
5. **Instagram Business Account ID** ❌ (You need this)

---

## 🔧 How to Get Instagram Business Account ID

### Step 1: Connect Instagram to Facebook Page

1. Go to your Facebook Page
2. Go to **Settings** → **Instagram**
3. Connect your Instagram Business Account to the Page
4. Make sure it's a **Business Account** (not Personal)

### Step 2: Get Instagram Business Account ID

**Method 1: Via Facebook Graph API Explorer**
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your App
3. Get a Page Access Token with `instagram_basic` permission
4. Make this API call:
   ```
   GET /{page-id}?fields=instagram_business_account
   ```
5. The response will have `instagram_business_account.id` - that's your Instagram Business Account ID

**Method 2: Via Facebook Page Settings**
1. Go to your Facebook Page
2. Settings → Instagram
3. Your Instagram Business Account ID is shown there

**Method 3: Via API (if you have Page Access Token)**
```bash
curl -X GET "https://graph.facebook.com/v18.0/{page-id}?fields=instagram_business_account&access_token={page-access-token}"
```

---

## 🔑 Facebook App Secret

You need your Facebook App Secret:

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your App (ID: `421181512329379`)
3. Go to **Settings** → **Basic**
4. Find **App Secret**
5. Click **Show** (you may need to verify your identity)
6. Copy the secret

---

## ✅ What You Have vs What You Need

### ✅ You Have:
- Facebook App ID: `421181512329379`
- Facebook Page ID: `617021748762367`
- Facebook Page Access Token: (You have one)

### ❌ You Need:
- Facebook App Secret
- Instagram Business Account ID

---

## 🚀 Quick Setup Steps

1. **Get Facebook App Secret**
   - Facebook Developers → Your App → Settings → Basic → App Secret

2. **Get Instagram Business Account ID**
   - Connect Instagram Business Account to your Facebook Page
   - Use Graph API Explorer or Page Settings to get the ID

3. **Add to MY_CONFIG.json**
   ```json
   {
     "api_keys": {
       "facebook_app_secret": "YOUR_APP_SECRET",
       "instagram_business_account_id": "YOUR_INSTAGRAM_BUSINESS_ACCOUNT_ID"
     }
   }
   ```

4. **Load Config**
   - Click "Load from MY_CONFIG.json" in Config page
   - Or run: `python scripts/load_config.py`

---

## 📝 Note About Instagram Access Token

For Instagram Graph API (posting content), you typically **don't need a separate Instagram Access Token**. 

The **Facebook Page Access Token** you have should work, as long as:
- Your Instagram Business Account is connected to the Facebook Page
- The Page Access Token has `instagram_content_publish` permission

However, if you want to use a dedicated Instagram Access Token:
1. Use the Facebook Page Access Token to get Instagram Business Account info
2. The Instagram API will use the Page Access Token for authentication

---

## 🧪 Testing

Once you have:
- Facebook App Secret
- Instagram Business Account ID

We can test:
1. ✅ LinkedIn native video upload (you have credentials)
2. ✅ Facebook native video upload (you have credentials)
3. ⏳ Instagram native video upload (need Business Account ID)

---

**Next Step**: Get your Facebook App Secret and Instagram Business Account ID, then add them to `MY_CONFIG.json`!

