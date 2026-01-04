# How to Get LinkedIn Access Token and Person URN

## 📋 Overview

To post videos to LinkedIn, you need:
1. **LinkedIn Client ID** ✅ (You have: `86vimp2gbw3c06`)
2. **LinkedIn Client Secret** ✅ (You have: `bNKWlrj1yCij5jUO`)
3. **LinkedIn Access Token** ❌ (You need this)
4. **LinkedIn Person URN** ❌ (You need this)

## 🔑 Method 1: LinkedIn OAuth Playground (Easiest)

### Step 1: Go to LinkedIn OAuth Playground
1. Visit: https://www.linkedin.com/developers/tools/oauth-playground
2. You'll need to be logged into LinkedIn

### Step 2: Configure OAuth Playground
1. **Select Your App:**
   - In the dropdown, select your app (or create a new one)
   - Your App ID: `86vimp2gbw3c06`

2. **Add Redirect URL:**
   - Add: `https://www.linkedin.com/developers/tools/oauth-playground`
   - Or use: `http://localhost:8080/callback` (if using our script)

3. **Select Permissions:**
   - Check these scopes:
     - ✅ `w_member_social` (Post, comment, and share on behalf of the user)
     - ✅ `r_liteprofile` (Read basic profile information)
     - ✅ `r_emailaddress` (Read email address)

### Step 3: Get Access Token
1. Click **"Request Token"** button
2. Authorize the app if prompted
3. Copy the **Access Token** that appears

### Step 4: Get Person URN
1. Use the Access Token to get your Person URN
2. Visit: `https://api.linkedin.com/v2/me?oauth2_access_token=YOUR_ACCESS_TOKEN`
3. Look for the `id` field - that's your Person URN
4. Format: `urn:li:person:xxxxx`

---

## 🔑 Method 2: Using Our Script (Automated)

We have a script that automates this process:

```bash
.venv/bin/python3 scripts/get_linkedin_token.py
```

This will:
1. Open browser for OAuth
2. Get Access Token automatically
3. Get Person URN automatically
4. Save to `MY_CONFIG.json`

---

## 🔑 Method 3: Manual API Call

### Step 1: Get Access Token via OAuth

1. **Build OAuth URL:**
   ```
   https://www.linkedin.com/oauth/v2/authorization?
     response_type=code&
     client_id=86vimp2gbw3c06&
     redirect_uri=YOUR_REDIRECT_URI&
     scope=w_member_social%20r_liteprofile%20r_emailaddress&
     state=random_state_string
   ```

2. **Authorize:**
   - Visit the URL in your browser
   - Log in and authorize
   - You'll be redirected with a `code` parameter

3. **Exchange Code for Token:**
   ```
   POST https://www.linkedin.com/oauth/v2/accessToken
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=authorization_code&
   code=YOUR_AUTHORIZATION_CODE&
   redirect_uri=YOUR_REDIRECT_URI&
   client_id=86vimp2gbw3c06&
   client_secret=bNKWlrj1yCij5jUO
   ```

4. **Response will contain:**
   ```json
   {
     "access_token": "YOUR_ACCESS_TOKEN",
     "expires_in": 5184000
   }
   ```

### Step 2: Get Person URN

1. **Call LinkedIn API:**
   ```
   GET https://api.linkedin.com/v2/me
   Authorization: Bearer YOUR_ACCESS_TOKEN
   ```

2. **Response:**
   ```json
   {
     "id": "urn:li:person:xxxxx",
     "firstName": {...},
     "lastName": {...}
   }
   ```

3. **Copy the `id` field** - that's your Person URN

---

## 📝 Quick Steps Summary

### Using OAuth Playground (Recommended):
1. Go to: https://www.linkedin.com/developers/tools/oauth-playground
2. Select your app
3. Check permissions: `w_member_social`, `r_liteprofile`
4. Click "Request Token"
5. Copy Access Token
6. Visit: `https://api.linkedin.com/v2/me?oauth2_access_token=YOUR_TOKEN`
7. Copy the `id` field (Person URN)

### Using Our Script:
```bash
.venv/bin/python3 scripts/get_linkedin_token.py
```

---

## ⚠️ Important Notes

1. **Access Token Expires:**
   - Standard tokens expire in 60 days
   - You'll need to refresh or get a new one

2. **Person URN Format:**
   - Must be: `urn:li:person:xxxxx`
   - The `xxxxx` is your LinkedIn user ID

3. **Permissions Required:**
   - `w_member_social` - Required for posting
   - `r_liteprofile` - Required for getting Person URN

4. **App Review:**
   - Some permissions may require app review
   - `w_member_social` typically requires review

---

## 🚀 After Getting Credentials

Once you have both:

1. **Update MY_CONFIG.json:**
   ```json
   {
     "api_keys": {
       "linkedin_access_token": "YOUR_ACCESS_TOKEN",
       "linkedin_person_urn": "urn:li:person:xxxxx"
     }
   }
   ```

2. **Load Config:**
   ```bash
   .venv/bin/python3 scripts/load_config.py
   ```

3. **Test:**
   - Visit Config page
   - Verify credentials are saved
   - Test LinkedIn connection

---

**The easiest method is LinkedIn OAuth Playground - it handles everything for you!** 🚀

