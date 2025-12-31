#!/bin/bash

# Run YouTube Automation locally for testing

echo "🚀 Starting YouTube Automation - Local Testing"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "✅ Virtual environment created"
fi

echo ""
echo "Installing/updating dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "Initializing database..."
python3 -c "from database import init_database; init_database()" 2>/dev/null || echo "Database will be created on first run"

echo ""
echo "=========================================="
echo "✅ Starting web server..."
echo "=========================================="
echo ""
echo "🌐 Open in your browser:"
echo "   http://localhost:5000"
echo ""
echo "📝 You can now:"
echo "   1. Configure API keys"
echo "   2. Set up automation schedule"
echo "   3. Test all features"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python3 app.py

