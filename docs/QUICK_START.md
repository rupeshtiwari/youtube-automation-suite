# Quick Start - Single Server Setup

## ✅ Simple Deployment (One Server, One Port)

The app now runs as **a single Flask server** on port 5001. Much simpler!

## Run the App

### Step 1: Build React Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### Step 2: Start Flask Server
```bash
python3 run.py
```

Or use the convenience script:
```bash
./build_and_run.sh
```

### Step 3: Access the App
Open browser: `http://localhost:5001`

That's it! One server, one port, simple deployment.

## Architecture

- **Port**: 5001 (single port for everything)
- **Frontend**: React app (built) served as static files from Flask
- **Backend**: Flask API at `/api/*` routes
- **Routing**: React Router handles frontend routes, Flask serves `index.html` for all non-API routes

## Deployment to NAS

1. Copy project to NAS
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && npm run build && cd ..
   ```
3. Run: `python3 run.py`

See `DEPLOY_NAS.md` for detailed NAS deployment guide.
