#!/bin/bash

# Restart Both React Frontend and Flask Backend

echo "🛑 Stopping existing servers..."

# Kill React/Vite processes
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null

# Kill Flask processes
pkill -f "python run.py" 2>/dev/null
pkill -f "flask run" 2>/dev/null

# Wait for processes to stop
sleep 2

echo "✅ Servers stopped"
echo ""
echo "🚀 Starting servers..."

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Start React in background
echo "Starting React frontend on http://localhost:5173..."
cd frontend
npm run dev > /tmp/react-dev.log 2>&1 &
REACT_PID=$!
cd ..

# Start Flask in background
echo "Starting Flask backend on http://localhost:5001..."
python run.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!

# Wait a moment for servers to start
sleep 3

echo ""
echo "✅ Servers started!"
echo ""
echo "📊 Process IDs:"
echo "   React: PID $REACT_PID"
echo "   Flask: PID $FLASK_PID"
echo ""
echo "🌐 Open: http://localhost:5173"
echo ""
echo "📝 Logs:"
echo "   React: tail -f /tmp/react-dev.log"
echo "   Flask: tail -f /tmp/flask.log"
echo ""
echo "🛑 To stop: kill $REACT_PID $FLASK_PID"

