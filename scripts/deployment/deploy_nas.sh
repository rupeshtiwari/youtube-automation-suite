#!/bin/bash

# NAS Deployment Script
# This script helps deploy YouTube Automation to your NAS

set -e

echo "🏠 YouTube Automation - NAS Deployment"
echo "========================================"
echo ""

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "✅ Docker found"
    USE_DOCKER=true
else
    echo "⚠️  Docker not found, will use direct Python"
    USE_DOCKER=false
fi

# Create data directory
echo ""
echo "📁 Creating data directory..."
mkdir -p data
mkdir -p exports
mkdir -p logs

# Set permissions
chmod 755 data exports logs

echo "✅ Directories created"
echo ""

# Check for required files
echo "🔍 Checking required files..."
MISSING_FILES=()

if [ ! -f "client_secret.json" ]; then
    MISSING_FILES+=("client_secret.json")
fi

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found (optional, but recommended)"
    echo "   Create .env file with your API keys"
fi

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "❌ Missing required files:"
    for file in "${MISSING_FILES[@]}"; do
        echo "   - $file"
    done
    echo ""
    echo "Please add these files before deploying"
    exit 1
fi

echo "✅ All required files present"
echo ""

# Deploy based on method
if [ "$USE_DOCKER" = true ]; then
    echo "🐳 Deploying with Docker..."
    echo ""
    
    # Build image
    echo "Building Docker image..."
    docker build -t youtube-automation:latest .
    
    echo ""
    echo "Starting container..."
    docker-compose up -d
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📊 Container status:"
    docker ps | grep youtube-automation || echo "Container not running"
    echo ""
    echo "📝 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🌐 Access web interface:"
    echo "   http://your-nas-ip:5000"
else
    echo "🐍 Deploying with Python directly..."
    echo ""
    echo "⚠️  Make sure Python 3.8+ and dependencies are installed"
    echo ""
    echo "Install dependencies:"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "Run application:"
    echo "   python app.py"
    echo ""
    echo "Or use systemd service (see NAS_DEPLOYMENT.md)"
fi

echo ""
echo "📚 For more details, see NAS_DEPLOYMENT.md"

