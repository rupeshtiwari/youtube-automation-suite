#!/bin/bash
# Quick restart script for YouTube Automation app
# This ensures a clean restart without port conflicts

set -e

echo "🛑 Stopping all servers..."

# Kill Flask server on port 5001
lsof -ti:5001 | xargs kill 2>/dev/null || true

# Kill Vite dev server on port 5173
pkill -f "vite" 2>/dev/null || true
lsof -ti:5173 | xargs kill 2>/dev/null || true

# Wait for processes to stop
sleep 2

echo "✅ All servers stopped"
echo ""
echo "🔨 Building React frontend..."

# Build React frontend
cd "$(dirname "$0")"
cd frontend
npm run build
cd ..

echo "✅ Frontend built"
echo ""
echo "🚀 Starting Flask server..."

# Activate virtual environment and start server
source .venv/bin/activate
python run.py

