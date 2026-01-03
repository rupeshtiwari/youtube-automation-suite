# How to Restart the App - Complete Guide

## 🛑 Step 1: Stop the Current Server

```bash
# Kill any process running on port 5001
lsof -ti:5001 | xargs kill 2>/dev/null

# Or if that doesn't work, find and kill manually:
ps aux | grep "python.*run.py" | grep -v grep | awk '{print $2}' | xargs kill 2>/dev/null

# Wait a moment for processes to stop
sleep 2
```

## 🔄 Step 2: Rebuild React Frontend (if you made frontend changes)

```bash
cd /Users/rupesh/code/youtube-automation/frontend
npm run build
cd ..
```

## 🚀 Step 3: Start the Server

### Option A: Using the run script (Recommended)
```bash
cd /Users/rupesh/code/youtube-automation
source .venv/bin/activate
python run.py
```

### Option B: Run in background
```bash
cd /Users/rupesh/code/youtube-automation
source .venv/bin/activate
python run.py > /tmp/app.log 2>&1 &
```

### Option C: Using the convenience script
```bash
cd /Users/rupesh/code/youtube-automation
./build_and_run.sh
```

## ✅ Step 4: Verify Server is Running

```bash
# Check if server is running on port 5001
lsof -i:5001

# Or test with curl
curl http://localhost:5001/health

# Or check the logs
tail -f /tmp/app.log
```

## 🌐 Step 5: Access the App

Open your browser and go to: **http://localhost:5001**

## 🔧 Quick Restart Command (All-in-One)

```bash
cd /Users/rupesh/code/youtube-automation && \
lsof -ti:5001 | xargs kill 2>/dev/null; \
sleep 2; \
source .venv/bin/activate && \
cd frontend && npm run build && cd .. && \
python run.py
```

## 📝 Troubleshooting

### If port 5001 is still in use:
```bash
# Find what's using the port
lsof -i:5001

# Kill it forcefully
kill -9 $(lsof -ti:5001)
```

### If you get "Module not found" errors:
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt
```

### If React build fails:
```bash
cd frontend
rm -rf node_modules dist
npm install
npm run build
cd ..
```

### If database errors occur:
```bash
# The database will be recreated automatically
# But you can check if it exists:
ls -la data/automation.db
```

## 🎯 What Gets Restarted

- ✅ Flask backend server
- ✅ All API endpoints
- ✅ Database connections
- ✅ Scheduled jobs
- ✅ React frontend (if rebuilt)

## 📍 Server Location

- **Port**: 5001
- **URL**: http://localhost:5001
- **Logs**: Check terminal output or `/tmp/app.log` if running in background
- **Database**: `data/automation.db`

