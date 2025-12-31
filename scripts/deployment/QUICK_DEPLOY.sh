#!/bin/bash

# Quick Deploy Script - Run from Your Mac
# This script helps you deploy to NAS from your local machine

set -e

echo "🚀 YouTube Automation - Quick Deploy to NAS"
echo "==========================================="
echo ""

# Get NAS details
read -p "Enter your NAS IP address (e.g., 192.168.88.17): " NAS_IP
read -p "Enter your NAS username (default: admin): " NAS_USER
NAS_USER=${NAS_USER:-admin}

echo ""
echo "📋 Deployment Summary:"
echo "   NAS IP: $NAS_IP"
echo "   Username: $NAS_USER"
echo "   Target: /volume1/docker/youtube-automation"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 1
fi

echo ""
echo "Step 1: Copying files to NAS..."
echo ""

# Create directory on NAS first
ssh ${NAS_USER}@${NAS_IP} "mkdir -p /volume1/docker/youtube-automation"

# Copy files
scp -r *.py *.txt *.yml *.sh *.md templates ${NAS_USER}@${NAS_IP}:/volume1/docker/youtube-automation/ 2>/dev/null || true
scp -r Dockerfile .dockerignore ${NAS_USER}@${NAS_IP}:/volume1/docker/youtube-automation/ 2>/dev/null || true

echo "✅ Files copied"
echo ""

echo "Step 2: Running deployment on NAS..."
echo ""

# SSH and run deployment
ssh ${NAS_USER}@${NAS_IP} << EOF
cd /volume1/docker/youtube-automation
chmod +x synology_one_click.sh
./synology_one_click.sh
EOF

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your app at:"
echo "   http://${NAS_IP}:5000"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://${NAS_IP}:5000 in your browser"
echo "   2. Go to Configuration page"
echo "   3. Add your API keys"
echo "   4. Set up automation schedule"
echo ""

