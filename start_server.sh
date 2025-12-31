#!/bin/bash

# Start the YouTube Automation web server
# This script activates the virtual environment and starts the Flask app

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the Flask app
echo "Starting web server..."
echo "Open http://localhost:5000 in your browser"
python app.py

