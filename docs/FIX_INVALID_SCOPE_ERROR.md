# Fix LinkedIn "invalid_scope_error"

## 🔴 Error: "The requested permission scope is not valid"

This error occurs because the scopes you're requesting are not available/approved for your LinkedIn app.

## ✅ Solution - Step by Step

### Step 1: Enable Marketing Developer Platform Product

1. Go to: https://www.linkedin.com/developers/apps/86vimp2gbw3c06
2. Click the **"Products"** tab (in the left sidebar)
3. Find **"Marketing Developer Platform"**
4. Click **"Request access"** or **"Add product"**
5. Fill out the request form:
   - **Use case**: "Post content to LinkedIn for business marketing"
   - **Description**: "This application automates posting video content from YouTube to LinkedIn for business marketing purposes"
   - Accept terms and submit
6. **Wait for approval** (can be instant or 1-3 business days)

### Step 2: After Approval - Verify Scopes

Once Marketing Developer Platform is approved:

1. Go back to: https://www.linkedin.com/developers/apps/86vimp2gbw3c06
2. Click **"Auth"** tab
3. Under **"OAuth 2.0 scopes"**, you should now see available scopes
4. The scopes we need should be available:
   - `w_member_social` (for posting content)
   - `r_liteprofile` (for getting Person URN)
   - `r_emailaddress` (optional, for email)

### Step 3: Alternative - Use Available Scopes

If Marketing Developer Platform approval is taking too long, you can temporarily use scopes that don't require it:

**Available without Marketing Developer Platform:**
- `r_liteprofile` - Basic profile info
- `r_emailaddress` - Email address

**But you CANNOT post content** without `w_member_social`, which requires Marketing Developer Platform.

## 🔍 Current Status Check

Your app currently shows:
- ✅ Redirect URI: `http://localhost:5001/api/linkedin/oauth/callback` (correct)
- ✅ Client ID: `86vimp2gbw3c06` (correct)
- ❌ OAuth 2.0 scopes: "No permissions added" (THIS IS THE PROBLEM)

## 📋 What to Do Right Now

1. **Go to Products tab**: https://www.linkedin.com/developers/apps/86vimp2gbw3c06/products
2. **Enable Marketing Developer Platform**
3. **Wait for approval** (check email)
4. **Test again** after approval

## ⚠️ Important Notes

- Without Marketing Developer Platform, you cannot use `w_member_social` scope
- Without `w_member_social`, you cannot post content to LinkedIn
- The approval process is required by LinkedIn for security

## 🚀 After Approval

Once approved:
1. The scopes will become available
2. Your OAuth flow will work
3. You'll be able to post content to LinkedIn

