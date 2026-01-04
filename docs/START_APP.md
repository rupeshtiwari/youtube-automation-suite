# How to Start/Restart the App

## Quick Start (Two Terminals Required)

You need to run **both** the React frontend and Flask backend:

### Terminal 1: React Frontend
```bash
cd frontend
npm install  # Only needed first time
npm run dev
```
Frontend will run on: **http://localhost:5173**

### Terminal 2: Flask Backend
```bash
python run.py
```
Backend will run on: **http://localhost:5001**

---

## Restart Options

### Option 1: Manual Restart (Recommended)

**Stop both servers:**
- Press `Ctrl+C` in both terminals

**Start again:**
- Terminal 1: `cd frontend && npm run dev`
- Terminal 2: `python run.py`

### Option 2: Using Restart Script (Flask Only)

For Flask backend only:
```bash
python scripts/restart_server.py
```

**Note:** This only restarts Flask, not React. You still need to manually restart React.

### Option 3: Quick Restart Script (Both Servers)

Create a script to restart both:

**For macOS/Linux:**
```bash
# Save as restart_all.sh
#!/bin/bash
# Kill existing processes
pkill -f "npm run dev"
pkill -f "python run.py"
pkill -f "vite"

# Wait a moment
sleep 2

# Start React (in background)
cd frontend && npm run dev &

# Start Flask (in background)
cd .. && python run.py &
```

**Usage:**
```bash
chmod +x restart_all.sh
./restart_all.sh
```

---

## Development Workflow

1. **First Time Setup:**
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install
   cd ..
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

2. **Daily Development:**
   - Terminal 1: `cd frontend && npm run dev`
   - Terminal 2: `python run.py`
   - Open: http://localhost:5173

3. **After Code Changes:**
   - React: Auto-reloads (Hot Module Replacement)
   - Flask: Press `Ctrl+C` and restart with `python run.py`

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5001 (Flask)
lsof -ti:5001 | xargs kill -9

# Kill process on port 5173 (React)
lsof -ti:5173 | xargs kill -9
```

### React Not Starting
```bash
cd frontend
rm -rf node_modules
npm install
npm run dev
```

### Flask Not Starting
```bash
# Check if port is free
lsof -i:5001

# Kill if needed, then restart
python run.py
```

---

## Production Deployment

For production, you would:
1. Build React: `cd frontend && npm run build`
2. Serve static files with Flask or Nginx
3. Use Gunicorn for Flask: `gunicorn app.main:app`

But for development, use the two-terminal approach above.

