# Fix: Facebook App API Access Deactivated

## 🚨 Error Message
"Page access tokens cannot be generated: API access deactivated. To reactivate, go to the app dashboard."

## ✅ Solution: Reactivate Your App

### Step 1: Go to App Dashboard
1. Go to: https://developers.facebook.com/apps/
2. Select your app: `421181512329379`
3. You'll see a warning about API access being deactivated

### Step 2: Reactivate API Access
1. In your app dashboard, look for a banner or notification about deactivated access
2. Click **"Reactivate"** or **"Request Review"** button
3. You may need to:
   - Complete App Review
   - Add Privacy Policy URL
   - Add Terms of Service URL
   - Verify your business (if required)

### Step 3: Complete Required Information
Go to **Settings → Basic** and ensure:
- ✅ **App Display Name**: Set
- ✅ **Contact Email**: Valid email
- ✅ **Privacy Policy URL**: Public URL (required)
- ✅ **App Domains**: Your domains
- ✅ **Category**: Selected
- ✅ **Icon**: Uploaded

### Step 4: Submit for Review (if needed)
1. Go to **App Review → Permissions and Features**
2. Request access to:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_content_publish`
3. Submit for review

## 🔧 Alternative: Manual Token Entry

If reactivation takes time, you can manually enter tokens:

### Method 1: Get Token from Graph API Explorer (Manual)

1. **Go to:** https://developers.facebook.com/tools/explorer/
2. **Select your App** (even if deactivated, Explorer might still work)
3. **Get User Access Token:**
   - Click "Get Token" → "Get User Access Token"
   - Select permissions
   - Generate token
4. **Get Page Token Manually:**
   - Visit: `https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_USER_TOKEN`
   - Find your Page ID in the response
   - Copy the `access_token` for that page
5. **Update MY_CONFIG.json:**
   ```json
   {
     "api_keys": {
       "facebook_page_access_token": "YOUR_PAGE_TOKEN_HERE"
     }
   }
   ```
6. **Load config:**
   ```bash
   python3 scripts/load_config.py
   ```

### Method 2: Use Long-Lived Token

If you have a valid User Access Token, you can exchange it for a long-lived Page Token:

```bash
# Exchange User Token for Long-Lived Token
curl "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_USER_TOKEN"
```

Then get Page Token from the long-lived token.

## 📋 Quick Checklist

- [ ] Go to App Dashboard
- [ ] Click "Reactivate" or "Request Review"
- [ ] Complete all required app information
- [ ] Add Privacy Policy URL
- [ ] Submit for App Review (if needed)
- [ ] Wait for approval (can take 1-7 days)
- [ ] Try Graph API Explorer again

## ⚠️ Important Notes

1. **App Review Process:**
   - Can take 1-7 business days
   - Facebook reviews your app's use case
   - You may need to provide additional information

2. **Privacy Policy Required:**
   - Must be publicly accessible
   - Must explain what data you collect
   - Must explain how you use it

3. **Business Verification:**
   - May be required for certain permissions
   - Especially for `pages_manage_posts` and `instagram_content_publish`

## 🚀 After Reactivation

Once your app is reactivated:

1. **Test in Graph API Explorer:**
   - Go to: https://developers.facebook.com/tools/explorer/
   - Select your app
   - Try generating a token

2. **Run the script:**
   ```bash
   .venv/bin/python3 scripts/get_facebook_token_v2.py YOUR_USER_TOKEN
   ```

3. **Verify it works:**
   ```bash
   .venv/bin/python3 scripts/test_token_flow.py
   ```

## 💡 Temporary Workaround

While waiting for reactivation, you can:
1. Use a different Facebook App (if you have one)
2. Create a new Facebook App (takes 5 minutes)
3. Use manual token entry (see Method 1 above)

---

**The app needs to be reactivated in Facebook Developer Dashboard. This is a Facebook requirement, not a script issue.**

