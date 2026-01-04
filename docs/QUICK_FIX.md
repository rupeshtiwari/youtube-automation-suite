# Quick Fix: Your Facebook Token is Expired

## ⚠️ Current Issue

Your Facebook Page Access Token is **expired or invalid**. The error message says:
```
The access token could not be decrypted
```

## ✅ Quick Solution

### Step 1: Get New Token (2 minutes)

1. **Go to:** https://developers.facebook.com/tools/explorer/
2. **Select App:** `421181512329379` (in the dropdown)
3. **Add Permissions:**
   - Click permissions dropdown
   - Add: `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`
4. **Generate Token:**
   - Click "Generate Access Token"
   - Authorize if needed
   - **Copy the token**

5. **Get Page Token:**
   - The token you got is a User Token
   - To get Page Token, use this URL (replace `{token}` with your token):
   ```
   https://graph.facebook.com/v18.0/me/accounts?access_token={token}
   ```
   - Find your Page ID `617021748762367` in the response
   - Copy the `access_token` for that page

### Step 2: Update Config

1. **Open `MY_CONFIG.json`**
2. **Replace the `facebook_page_access_token` value** with your new token
3. **Save the file**

### Step 3: Load Config

```bash
python3 scripts/load_config.py
```

### Step 4: Test Instagram Account ID

```bash
python3 scripts/get_instagram_account_id.py
```

---

## 🎯 What You'll Get

After fixing the token, you'll be able to:
- ✅ Get your Instagram Business Account ID
- ✅ Test Facebook video uploads
- ✅ Test Instagram video uploads

---

## 📋 Still Need

- [ ] Facebook App Secret (for Instagram)
- [ ] Instagram Business Account ID (will get after token fix)
- [ ] LinkedIn Access Token (for LinkedIn testing)

---

**Once you get the new token, update `MY_CONFIG.json` and tell me!** 🚀

