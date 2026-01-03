# Deploy to NAS - Simple Guide

## Overview
This app now runs as a **single Flask server** on one port (5001). Much simpler to deploy!

## Quick Start

### 1. Build the React App
```bash
cd frontend
npm install
npm run build
cd ..
```

### 2. Run the Server
```bash
python3 run.py
```

Or use the convenience script:
```bash
./build_and_run.sh
```

### 3. Access the App
Open your browser to: `http://localhost:5001`

## Deployment to NAS

### Option 1: Direct Python (Simplest)
1. Copy entire project to your NAS
2. Install Python 3 and dependencies:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && npm run build && cd ..
   ```
3. Run: `python3 run.py`

### Option 2: Using systemd (Auto-start on boot)
Create `/etc/systemd/system/youtube-automation.service`:
```ini
[Unit]
Description=YouTube Automation App
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/youtube-automation
ExecStart=/usr/bin/python3 run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable youtube-automation
sudo systemctl start youtube-automation
```

### Option 3: Docker (Recommended for NAS)
See `docker-compose.yml` and `Dockerfile` for containerized deployment.

## Single Server Architecture

- **Port**: 5001 (configurable in `run.py`)
- **Frontend**: Served as static files from Flask (built React app)
- **Backend**: Flask API endpoints at `/api/*`
- **Routing**: React Router handles frontend routes, Flask serves `index.html` for all non-API routes

## Important Files

- `run.py` - Server entry point
- `frontend/dist/` - Built React app (created after `npm run build`)
- `app/main.py` - Flask app with all routes
- `requirements.txt` - Python dependencies

## Configuration

All settings are stored in the database (`youtube_automation.db`) and persist across restarts.

## Troubleshooting

1. **Port already in use**: Change port in `run.py`
2. **Build errors**: Make sure Node.js is installed for `npm run build`
3. **Import errors**: Install Python dependencies: `pip install -r requirements.txt`

