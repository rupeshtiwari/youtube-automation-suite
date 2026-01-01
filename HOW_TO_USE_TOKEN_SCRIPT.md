# How to Use the Facebook Token Script

## ✅ The Script IS Working!

The script is working correctly. When you run it without a token, it shows instructions. That's expected behavior!

## 📋 Step-by-Step Usage

### Step 1: Get User Access Token from Graph API Explorer

1. **Open:** https://developers.facebook.com/tools/explorer/
2. **Select your App:** Click dropdown (top right) → Select `421181512329379`
3. **Get Token:**
   - Click "Get Token" button (top right)
   - Select "Get User Access Token"
   - Check these permissions:
     - ✅ pages_manage_posts
     - ✅ pages_read_engagement
     - ✅ pages_show_list
     - ✅ instagram_basic
     - ✅ instagram_content_publish
     - ✅ business_management
   - Click "Generate Access Token"
   - Authorize if prompted
   - **Copy the token** (long string that appears)

### Step 2: Run Script with Your Token

```bash
# Activate venv
source .venv/bin/activate

# Run script with your token
python3 scripts/get_facebook_token_v2.py YOUR_TOKEN_HERE
```

**Example:**
```bash
python3 scripts/get_facebook_token_v2.py YOUR_TOKEN_FROM_GRAPH_API_EXPLORER
```

### Step 3: Script Will Automatically

1. ✅ Get Page Access Token from your User Token
2. ✅ Get Instagram Business Account ID (if connected)
3. ✅ Save everything to `MY_CONFIG.json`
4. ✅ Save to database

## 🧪 Test Current Token

To test if your existing token is valid:

```bash
.venv/bin/python3 scripts/test_token_flow.py
```

## ❓ Common Questions

### Q: Why does it just show instructions?
**A:** Because you didn't provide a token! The script needs a User Access Token from Graph API Explorer.

### Q: Can you get the token automatically?
**A:** No, Facebook requires you to authorize in your browser. That's why we use Graph API Explorer - it's the easiest way.

### Q: What if I get "Facebook Login unavailable"?
**A:** That's why we use Graph API Explorer instead of OAuth! Graph API Explorer works even when OAuth doesn't.

## 📝 Quick Reference

```bash
# Show instructions (no token)
.venv/bin/python3 scripts/get_facebook_token_v2.py

# Run with token (replace YOUR_TOKEN)
.venv/bin/python3 scripts/get_facebook_token_v2.py YOUR_TOKEN

# Or use environment variable
FACEBOOK_USER_TOKEN=YOUR_TOKEN .venv/bin/python3 scripts/get_facebook_token_v2.py
```

---

**The script is ready - you just need to get a User Access Token from Graph API Explorer and provide it!** 🚀

