# 🖥️ Run Locally - Quick Start

## 🚀 Start the Web UI

Run this command:

```bash
cd /Users/rupesh/code/youtube-automation
./run_local.sh
```

Or manually:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python app.py
```

## 🌐 Access the UI

Once started, open in your browser:

```
http://localhost:5000
```

## 📝 What You Can Do

1. **Dashboard**: View automation status
2. **Configuration**: 
   - Enter API keys (LinkedIn, Facebook, Instagram, Ayrshare)
   - Set up scheduling (videos per day, schedule time, etc.)
   - Enable/disable automation
   - Choose database or Excel

3. **Test**: Click "Run Now" to test automation

## 🔧 First Time Setup

The app will:
- ✅ Create database automatically
- ✅ Create settings file
- ✅ Initialize everything

## ⚠️ Important Files

Make sure you have:
- `client_secret.json` - Google OAuth credentials (optional for now, can add later)
- `.env` - API keys (optional, can add via web UI)

## 🛑 Stop the Server

Press `Ctrl+C` in the terminal to stop.

---

**Ready? Run `./run_local.sh` and open http://localhost:5000**

