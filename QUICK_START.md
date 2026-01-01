# Quick Start Guide

## 🚀 Running Scripts

All scripts should be run with the virtual environment activated. You have two options:

### Option 1: Activate Virtual Environment Manually

```bash
# Activate virtual environment
source .venv/bin/activate

# Now run any script
python3 scripts/fetch_facebook_config.py
python3 scripts/get_instagram_account_id.py
python3 scripts/load_config.py
```

### Option 2: Use Helper Script (Easier)

```bash
# Use the helper script (automatically activates venv)
./scripts/run_with_venv.sh fetch_facebook_config.py
./scripts/run_with_venv.sh get_instagram_account_id.py
./scripts/run_with_venv.sh load_config.py
```

## 📋 Common Commands

### Fetch Facebook Configuration (OAuth)
```bash
./scripts/run_with_venv.sh fetch_facebook_config.py
```

### Get Instagram Account ID
```bash
./scripts/run_with_venv.sh get_instagram_account_id.py
```

### Load Configuration from File
```bash
./scripts/run_with_venv.sh load_config.py
```

## ⚠️ If You Get "ModuleNotFoundError"

If you see errors like `ModuleNotFoundError: No module named 'requests'`:

1. **Make sure virtual environment is activated:**
   ```bash
   source .venv/bin/activate
   ```

2. **Or install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Or use the helper script:**
   ```bash
   ./scripts/run_with_venv.sh <script_name>
   ```

## ✅ Your Prompt Should Show

When virtual environment is activated, you should see:
```
(.venv) ➜ youtube-automation
```

If you don't see `(.venv)`, the virtual environment is not activated!
