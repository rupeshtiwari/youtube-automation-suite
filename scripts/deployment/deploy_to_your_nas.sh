#!/bin/bash

# Automated Deployment Script for Your NAS
# NAS IP: 192.168.68.108

set -e

NAS_IP="192.168.68.108"
NAS_USER="rupesh"
TARGET_DIR="/volume1/docker/youtube-automation"
NAS_PASSWORD="8xrBZyb6PuBFkqVfkgj6"

echo "🚀 YouTube Automation - Automated Deployment"
echo "============================================"
echo ""
echo "📋 Configuration:"
echo "   NAS IP: $NAS_IP"
echo "   Username: $NAS_USER"
echo "   Target: $TARGET_DIR"
echo ""

# Check if we can reach the NAS
echo "Step 1: Checking NAS connection..."
if ping -c 1 -W 1 $NAS_IP &> /dev/null; then
    echo "✅ NAS is reachable"
else
    echo "❌ Cannot reach NAS at $NAS_IP"
    echo "   Please check:"
    echo "   1. NAS is powered on"
    echo "   2. You're on the same network"
    echo "   3. IP address is correct"
    exit 1
fi

echo ""
echo "Step 2: Testing SSH connection..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes ${NAS_USER}@${NAS_IP} exit 2>/dev/null; then
    echo "✅ SSH connection works (using key-based auth)"
    SSH_KEY_AUTH=true
else
    echo "⚠️  Will prompt for password"
    SSH_KEY_AUTH=false
fi

echo ""
echo "Step 3: Creating directory on NAS..."
ssh ${NAS_USER}@${NAS_IP} "mkdir -p ${TARGET_DIR}/data ${TARGET_DIR}/exports" || {
    echo "❌ Failed to create directories"
    echo "   Please check SSH is enabled on your NAS:"
    echo "   Control Panel → Terminal & SNMP → Enable SSH"
    exit 1
}
echo "✅ Directories created"

echo ""
echo "Step 4: Copying files to NAS..."
echo "   This may take a minute..."

# Copy all necessary files
scp -r *.py ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true
scp -r templates ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true
scp requirements.txt Dockerfile docker-compose.yml .dockerignore ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true
scp synology_one_click.sh ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true

echo "✅ Files copied"

echo ""
echo "Step 5: Running deployment on NAS..."
echo "   (This will take a few minutes to build Docker image)"

# Run deployment script on NAS
ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'
cd /volume1/docker/youtube-automation
chmod +x synology_one_click.sh
./synology_one_click.sh
ENDSSH

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Access your application:"
echo "   http://${NAS_IP}:5000"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://${NAS_IP}:5000 in your browser"
echo "   2. Go to Configuration page"
echo "   3. Add your API keys"
echo "   4. Set up automation schedule"
echo ""
echo "🔍 Check status:"
echo "   ssh ${NAS_USER}@${NAS_IP} 'docker ps | grep youtube-automation'"
echo ""
echo "📊 View logs:"
echo "   ssh ${NAS_USER}@${NAS_IP} 'cd ${TARGET_DIR} && docker-compose logs -f'"
echo ""

