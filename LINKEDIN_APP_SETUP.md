# 🔧 LinkedIn App Setup - Enable Required Products

## Problem
Your LinkedIn app doesn't have any scopes available. You need to enable the required products first.

## Solution: Enable Marketing Developer Platform

### Step 1: Go to Your App Settings
1. Go to: https://www.linkedin.com/developers/apps
2. Click on your app: **FullStack Master** (Client ID: 86vimp2gbw3c06)
3. Or go directly to: https://www.linkedin.com/developers/apps/86vimp2gbw3c06

### Step 2: Request Product Access
1. In your app dashboard, look for **"Products"** section
2. Click **"Request access"** or **"Add product"** for:
   - ✅ **Marketing Developer Platform** (Required for posting)
   - ✅ **Sign In with LinkedIn using OpenID Connect** (Optional, for profile access)

### Step 3: Fill Out Product Request Form
For **Marketing Developer Platform**:
- **Use case**: "I want to post content to LinkedIn on behalf of my business"
- **Description**: "Automated posting of video content from YouTube to LinkedIn for business marketing"
- **Accept terms** and submit

### Step 4: Wait for Approval
- LinkedIn may approve immediately (for some apps)
- Or may take 1-3 business days
- You'll get an email when approved

### Step 5: After Approval
1. Go back to: https://www.linkedin.com/developers/tools/oauth-playground
2. Select your app: **FullStack Master**
3. You should now see scopes available:
   - ✅ `w_member_social` (Post, comment, and share)
   - ✅ `r_liteprofile` (Read basic profile)
4. Select these scopes
5. Click **"Request access token"**
6. Copy the token

---

## Alternative: Use Direct OAuth Flow (No Playground Needed)

If you can't get product access approved, use our automated script:

```bash
.venv/bin/python3 scripts/get_linkedin_token.py
```

This script:
- Opens browser for OAuth
- Handles the full OAuth flow
- Gets token automatically
- Gets Person URN automatically
- Saves everything

**But you still need to enable Marketing Developer Platform product first!**

---

## Quick Checklist

- [ ] Go to app settings: https://www.linkedin.com/developers/apps/86vimp2gbw3c06
- [ ] Request access to "Marketing Developer Platform"
- [ ] Wait for approval (may be instant or 1-3 days)
- [ ] Go back to OAuth Playground
- [ ] Select scopes: `w_member_social`, `r_liteprofile`
- [ ] Get access token
- [ ] Get Person URN using: `https://api.linkedin.com/v2/me?oauth2_access_token=YOUR_TOKEN`

---

## If Product Request is Denied

LinkedIn may require:
- Business verification
- More detailed use case
- App review process

In that case, you can:
1. Use the automated OAuth script (still needs product access)
2. Or use LinkedIn's official API documentation for manual setup
3. Or contact LinkedIn Developer Support

---

**The key issue**: Your app needs "Marketing Developer Platform" product enabled to get the `w_member_social` scope for posting.

