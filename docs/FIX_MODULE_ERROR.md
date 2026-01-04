# Fix: ModuleNotFoundError: No module named 'requests'

## ✅ Solution

You need to activate the virtual environment before running scripts. Here are **3 easy ways**:

### Method 1: Activate Virtual Environment (Recommended)

```bash
# Activate virtual environment
source .venv/bin/activate

# Your prompt should now show (.venv)
# Now run any script
python3 scripts/get_instagram_account_id.py
python3 scripts/fetch_facebook_config.py
```

### Method 2: Use Helper Script (Easiest)

```bash
# Helper script automatically activates venv
./scripts/run_with_venv.sh get_instagram_account_id.py
./scripts/run_with_venv.sh fetch_facebook_config.py
```

### Method 3: Use Full Path to Venv Python

```bash
# Use the virtual environment's Python directly
.venv/bin/python3 scripts/get_instagram_account_id.py
.venv/bin/python3 scripts/fetch_facebook_config.py
```

## ✅ Verify Virtual Environment is Active

When activated, your prompt should show:
```
(.venv) ➜ youtube-automation
```

If you **don't see `(.venv)`**, the virtual environment is **not activated**!

## 📋 Quick Commands

### Get Instagram Account ID
```bash
source .venv/bin/activate
python3 scripts/get_instagram_account_id.py
```

### Fetch Facebook Config (OAuth)
```bash
source .venv/bin/activate
python3 scripts/fetch_facebook_config.py
```

### Load Config
```bash
source .venv/bin/activate
python3 scripts/load_config.py
```

## ⚠️ Note About Token

The script ran successfully, but your **Facebook Page Access Token is expired**. 

To fix this, run:
```bash
source .venv/bin/activate
python3 scripts/fetch_facebook_config.py
```

This will:
1. Open browser for OAuth
2. Get new token automatically
3. Fetch Instagram Account ID
4. Save everything

---

**That's it!** Always activate the virtual environment first, or use the helper script! 🚀

