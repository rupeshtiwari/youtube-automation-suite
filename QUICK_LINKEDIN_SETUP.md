# 🚀 Quick LinkedIn Setup Guide

## Method 1: LinkedIn OAuth Playground (EASIEST - 2 minutes)

### Step 1: Get Access Token
1. **Go to**: https://www.linkedin.com/developers/tools/oauth-playground
2. **Select your app** in the dropdown (or create one if needed)
3. **Add Redirect URL** (if not already added):
   - `https://www.linkedin.com/developers/tools/oauth-playground`
4. **Select Permissions**:
   - ✅ `w_member_social` (Post, comment, and share)
   - ✅ `r_liteprofile` (Read basic profile)
5. **Click "Request Token"**
6. **Authorize** if prompted
7. **Copy the Access Token** (long string that appears)

### Step 2: Get Person URN
1. **Open a new browser tab**
2. **Visit this URL** (replace YOUR_TOKEN with the token you copied):
   ```
   https://api.linkedin.com/v2/me?oauth2_access_token=YOUR_TOKEN
   ```
3. **You'll see JSON response** like:
   ```json
   {
     "id": "urn:li:person:xxxxx",
     "firstName": {...},
     "lastName": {...}
   }
   ```
4. **Copy the `id` field** - that's your Person URN (format: `urn:li:person:xxxxx`)

### Step 3: Update Your Config
1. **Open** `MY_CONFIG.json`
2. **Update** these fields:
   ```json
   {
     "api_keys": {
       "linkedin_access_token": "PASTE_YOUR_TOKEN_HERE",
       "linkedin_person_urn": "urn:li:person:xxxxx"
     }
   }
   ```
3. **Save** the file
4. **Restart** your server (or the app will auto-load on next startup)

---

## Method 2: Using Our Script (Automated)

```bash
.venv/bin/python3 scripts/get_linkedin_token.py
```

This will:
- Open browser for OAuth
- Get Access Token automatically
- Get Person URN automatically
- Save to database and MY_CONFIG.json

**Note**: Make sure your LinkedIn app has the redirect URL configured:
- `http://localhost:8080/callback`

---

## Method 3: Manual API Call (If OAuth Playground doesn't work)

### Step 1: Build OAuth URL
Visit this URL in your browser (replace YOUR_REDIRECT_URI):
```
https://www.linkedin.com/oauth/v2/authorization?
  response_type=code&
  client_id=86vimp2gbw3c06&
  redirect_uri=YOUR_REDIRECT_URI&
  scope=w_member_social%20r_liteprofile&
  state=random123
```

### Step 2: Get Authorization Code
- After authorizing, you'll be redirected with a `code` parameter
- Copy that code

### Step 3: Exchange Code for Token
Use curl or Postman:
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -d "grant_type=authorization_code" \
  -d "code=YOUR_CODE" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "client_id=86vimp2gbw3c06" \
  -d "client_secret=bNKWlrj1yCij5jUO"
```

### Step 4: Get Person URN
```bash
curl -X GET "https://api.linkedin.com/v2/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## ⚠️ Troubleshooting

### "Invalid redirect_uri"
- Make sure redirect URI is added in LinkedIn app settings
- Must match exactly (including http vs https)

### "Invalid client_id"
- Check your Client ID: `86vimp2gbw3c06`
- Make sure app is active in LinkedIn Developers

### "Access token expired"
- LinkedIn tokens expire in 60 days
- Get a new token using the same method

### "Person URN not found"
- Make sure you're using the `/v2/me` endpoint
- Check that token has `r_liteprofile` permission

---

## ✅ Quick Checklist

- [ ] Got Access Token from OAuth Playground
- [ ] Got Person URN from `/v2/me` API
- [ ] Updated `MY_CONFIG.json` with both values
- [ ] Restarted server (or wait for auto-load)
- [ ] Verified in Config page that values are saved

---

**Recommended**: Use Method 1 (OAuth Playground) - it's the fastest and easiest! 🚀

