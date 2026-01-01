#!/bin/bash
# Helper script to run Python scripts with virtual environment activated

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the script passed as argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <script_name> [args...]"
    echo "Example: $0 get_instagram_account_id.py"
    exit 1
fi

SCRIPT_NAME="$1"
shift

if [ ! -f "scripts/$SCRIPT_NAME" ]; then
    echo "❌ Script not found: scripts/$SCRIPT_NAME"
    exit 1
fi

echo "🚀 Running: scripts/$SCRIPT_NAME $@"
python3 "scripts/$SCRIPT_NAME" "$@"

