#!/bin/bash
# Build React app and run Flask server
# Simple single-server setup for deployment

set -e

echo "🔨 Building React app..."
cd frontend
npm install --silent
npm run build
cd ..

echo "✅ Build complete!"
echo "🚀 Starting Flask server on port 5001..."
echo ""
echo "Access the app at: http://localhost:5001"
echo ""

python3 run.py

