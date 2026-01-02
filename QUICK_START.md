# Quick Start Guide

## 🚀 Start the App (Two Terminals)

### Terminal 1: React Frontend
```bash
cd frontend
npm run dev
```
✅ Frontend: http://localhost:5173

### Terminal 2: Flask Backend
```bash
python run.py
```
✅ Backend: http://localhost:5001

---

## 🔄 Restart the App

### Method 1: Manual (Recommended)
1. Press `Ctrl+C` in both terminals
2. Start again:
   - Terminal 1: `cd frontend && npm run dev`
   - Terminal 2: `python run.py`

### Method 2: Restart Script (Both Servers)
```bash
./restart_all.sh
```

### Method 3: Flask Only
```bash
python scripts/restart_server.py
```

---

## 📝 Notes

- **React** auto-reloads on code changes (no restart needed)
- **Flask** needs restart after Python code changes
- Both servers must be running for the app to work
- Frontend proxies `/api/*` requests to Flask backend

---

## 🆘 Troubleshooting

**Port in use?**
```bash
# Kill Flask
lsof -ti:5001 | xargs kill -9

# Kill React
lsof -ti:5173 | xargs kill -9
```

**First time?**
```bash
cd frontend && npm install
pip install -r requirements.txt
```
