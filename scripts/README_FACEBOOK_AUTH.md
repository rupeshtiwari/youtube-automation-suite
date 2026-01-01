# Facebook Configuration Auto-Fetcher

## 🚀 Quick Start

Run this script to automatically fetch all Facebook configuration data using OAuth (just like YouTube authentication):

```bash
python3 scripts/fetch_facebook_config.py
```

## 📋 What It Does

This script will:

1. **Open your browser** for Facebook OAuth authorization
2. **Get User Access Token** automatically
3. **Fetch your Facebook Pages** and get Page Access Token
4. **Get Instagram Business Account ID** (if connected)
5. **Make tokens long-lived** (if App Secret is available)
6. **Update MY_CONFIG.json** and database automatically

## ✅ Prerequisites

1. **Facebook App ID** must be in `MY_CONFIG.json`:
   ```json
   {
     "api_keys": {
       "facebook_app_id": "YOUR_APP_ID"
     }
   }
   ```

2. **Facebook App Secret** (optional but recommended):
   - Add to `MY_CONFIG.json` for long-lived tokens
   - Or the script will prompt you to enter it

3. **Facebook Page ID** (optional):
   - If you know your Page ID, add it to config
   - Otherwise, script will let you choose from available pages

## 🔧 How It Works

### Step 1: Authorization
- Opens browser to Facebook OAuth
- You log in and authorize the app
- Script receives authorization code automatically

### Step 2: Get Tokens
- Exchanges authorization code for User Access Token
- Fetches your Facebook Pages
- Gets Page Access Token for your page

### Step 3: Get Instagram
- Fetches Instagram Business Account ID (if connected)
- Gets Instagram username

### Step 4: Long-Lived Tokens
- If App Secret is available, exchanges for long-lived token
- Long-lived tokens expire in ~60 days (vs 1 hour for short-lived)

### Step 5: Save Everything
- Updates `MY_CONFIG.json`
- Updates database
- Shows summary of what was fetched

## 📝 Example Output

```
==============================================================
🔑 Facebook Configuration Auto-Fetcher
==============================================================

📱 App ID: 421181512329379
📄 Page ID: 617021748762367

📋 Step 1: Getting Authorization
----------------------------------------------------------------------
🌐 Opening browser for Facebook authorization...
📝 Instructions:
   1. Log in to Facebook if needed
   2. Authorize the app
   3. You'll be redirected back automatically

⏳ Waiting for authorization...
✅ Authorization received!

📋 Step 2: Getting Access Token
----------------------------------------------------------------------
🔄 Exchanging authorization code for access token...
✅ Got User Access Token!

📋 Step 3: Getting Page Access Token
----------------------------------------------------------------------
🔍 Fetching your Facebook Pages...
✅ Found 1 page(s):
   Using only available page: My Page Name
✅ Selected page: My Page Name (ID: 617021748762367)
   Page Access Token: EAAFZCDZCZAtqKMBAHgd...

📋 Step 4: Getting Instagram Business Account ID
----------------------------------------------------------------------
🔍 Fetching Instagram Business Account...
✅ Found Instagram Business Account!
   Account ID: 17841405309211844
   Username: @myusername

📋 Step 5: Making Token Long-Lived
----------------------------------------------------------------------
🔄 Exchanging for long-lived token...
✅ Long-lived token created! (expires in 60 days)

📋 Step 6: Updating Configuration
----------------------------------------------------------------------
✅ Updated MY_CONFIG.json!

==============================================================
✅ Configuration Complete!
==============================================================

📝 Summary:
   ✅ Facebook Page Access Token: EAAFZCDZCZAtqKMBAHgd...
   ✅ Facebook Page ID: 617021748762367
   ✅ Facebook App Secret: ********************
   ✅ Instagram Business Account ID: 17841405309211844
   ✅ Instagram Username: @myusername

🚀 Next steps:
   1. Test Instagram: python3 scripts/get_instagram_account_id.py
   2. Test video uploads: Ready to test!
```

## ⚠️ Troubleshooting

### "No pages found"
- Make sure you have admin access to at least one Facebook Page
- Check that you authorized the app with `pages_manage_posts` permission

### "No Instagram Business Account found"
- Your Instagram account must be a **Business Account** (not Personal)
- Instagram must be connected to your Facebook Page
- Go to Facebook Page → Settings → Instagram to connect

### "Authorization failed"
- Make sure your App ID is correct
- Check that redirect URI is set correctly in Facebook App settings
- Make sure port 8080 is not in use

### "Could not exchange token"
- App Secret is required for long-lived tokens
- Add App Secret to `MY_CONFIG.json` or enter it when prompted

## 🔒 Security Notes

- Tokens are saved to `MY_CONFIG.json` (which is in `.gitignore`)
- Tokens are also saved to database (encrypted at rest)
- Never commit `MY_CONFIG.json` to Git
- Long-lived tokens expire in ~60 days (you'll need to refresh)

## 🎯 Next Steps

After running this script:

1. **Test Instagram Account ID:**
   ```bash
   python3 scripts/get_instagram_account_id.py
   ```

2. **Load config:**
   ```bash
   python3 scripts/load_config.py
   ```

3. **Test video uploads:**
   - LinkedIn: Need LinkedIn Access Token
   - Facebook: ✅ Ready!
   - Instagram: ✅ Ready!

---

**That's it!** The script handles everything automatically, just like YouTube OAuth! 🚀

