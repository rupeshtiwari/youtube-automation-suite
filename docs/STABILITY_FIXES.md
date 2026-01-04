# App Stability Fixes - Port 5173 Issue Resolved

## 🐛 Problem
The app was sometimes redirecting to port 5173 (Vite dev server) and crashing because:
1. Vite dev server was running in the background
2. `react_app.html` template was redirecting to port 5173
3. CORS was configured to allow port 5173
4. Routes were trying to use dev server instead of built static files

## ✅ Fixes Applied

### 1. Killed Vite Dev Server
- Stopped any running Vite processes on port 5173
- App now only uses built static files from `frontend/dist`

### 2. Removed react_app.html Template
- Deleted `templates/react_app.html` which was redirecting to port 5173
- All routes now properly serve Flask templates or React build

### 3. Fixed CORS Configuration
- Removed `localhost:5173` and `localhost:5174` from CORS origins
- Now only allows `localhost:5001` (production port) and `localhost:3000` (legacy)

### 4. Fixed /shorts Route
- Changed from serving `react_app.html` to serving React build or dashboard fallback
- No more redirects to dev server

### 5. Improved Catch-All Route
- Better error handling
- Explicitly excludes Flask routes
- Only serves React for client-side routes

## 🚀 How to Ensure Stability

### Always Use Built Files (Not Dev Server)

1. **Never run Vite dev server in production:**
   ```bash
   # DON'T run this when using Flask:
   cd frontend && npm run dev
   ```

2. **Always build before running Flask:**
   ```bash
   cd frontend && npm run build && cd ..
   python run.py
   ```

3. **Check for running Vite processes:**
   ```bash
   ps aux | grep vite
   # If found, kill them:
   pkill -f vite
   ```

### Proper Startup Sequence

```bash
# 1. Kill any dev servers
pkill -f vite
lsof -ti:5001 | xargs kill 2>/dev/null

# 2. Build React frontend
cd frontend && npm run build && cd ..

# 3. Start Flask server
source .venv/bin/activate
python run.py
```

## 🔍 Verification

After restart, verify:
1. ✅ No Vite processes running: `ps aux | grep vite`
2. ✅ Server on port 5001: `lsof -i:5001`
3. ✅ No redirects to 5173: Check browser network tab
4. ✅ App loads at http://localhost:5001

## 📝 Notes

- **Port 5173** = Vite dev server (development only)
- **Port 5001** = Flask production server (what you should use)
- The app should **NEVER** redirect to 5173 in production
- Always use `npm run build` before running Flask

