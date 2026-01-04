# How to Restart Server to See Latest Config

## 🔄 Restart Flask Server

The config page loads settings from the database when the server starts. If you've updated the database, you may need to restart the server to see changes.

### Step 1: Find Running Server

```bash
# Find Flask processes
ps aux | grep -i "python.*app\|flask" | grep -v grep
```

Or use the helper script:
```bash
python3 scripts/restart_server.py
```

### Step 2: Stop Current Server

If you see a process, stop it:
```bash
# Option 1: Press Ctrl+C in the terminal where server is running
# Option 2: Kill by PID
kill <PID>
```

### Step 3: Start Server

```bash
# Activate venv
source .venv/bin/activate

# Start server
python3 run.py
```

Or if you have a different entry point:
```bash
flask run --host=0.0.0.0 --port=5001
```

## ✅ After Restart

1. Visit: http://localhost:5001/config
2. All settings from database should be displayed
3. Fields should be prepopulated with your values

## 🔍 Verify Config is Loaded

Before restarting, verify settings are in database:
```bash
python3 scripts/verify_config_display.py
```

This confirms all settings are saved and will be displayed.

