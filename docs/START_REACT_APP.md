# Starting the Modern React App

## Prerequisites

1. **Node.js installed** (v20+ recommended)
   - Check: `node --version`
   - Install: https://nodejs.org/

2. **Python dependencies installed**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Terminal 1: React Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will run on: http://localhost:5173

### Terminal 2: Flask Backend
```bash
python run.py
```
Backend will run on: http://localhost:5001

## What's Different

- **Frontend**: Modern React app (Vite + TypeScript)
- **Backend**: Flask API (CORS enabled)
- **UI**: Tailwind CSS + modern components
- **Features**: PWA, responsive, dark mode

## Access

Open: http://localhost:5173

The React app will proxy `/api/*` requests to the Flask backend automatically.

