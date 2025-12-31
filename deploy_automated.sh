#!/bin/bash

# Fully Automated Deployment Script
# NAS: 192.168.68.108
# User: rupesh

set -e

NAS_IP="192.168.68.108"
NAS_USER="rupesh"
NAS_PASSWORD="8xrBZyb6PuBFkqVfkgj6"
TARGET_DIR="/volume1/docker/youtube-automation"

echo "🚀 YouTube Automation - Fully Automated Deployment"
echo "=================================================="
echo ""
echo "📋 Configuration:"
echo "   NAS IP: $NAS_IP"
echo "   Username: $NAS_USER"
echo "   Target: $TARGET_DIR"
echo ""

# Check if sshpass is available (for password authentication)
if command -v sshpass &> /dev/null; then
    echo "✅ sshpass found - will use password authentication"
    SSHPASS_CMD="sshpass -p '${NAS_PASSWORD}'"
    SSH_CMD="${SSHPASS_CMD} ssh -o StrictHostKeyChecking=no"
    SCP_CMD="${SSHPASS_CMD} scp -o StrictHostKeyChecking=no"
else
    echo "⚠️  sshpass not found"
    echo "   Installing sshpass or you'll be prompted for password..."
    echo ""
    echo "   On macOS, install with:"
    echo "   brew install hudochenkov/sshpass/sshpass"
    echo ""
    read -p "Continue anyway? (you'll enter password manually) (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    SSH_CMD="ssh -o StrictHostKeyChecking=no"
    SCP_CMD="scp -o StrictHostKeyChecking=no"
fi

# Check if we can reach the NAS
echo ""
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
if $SSH_CMD ${NAS_USER}@${NAS_IP} "echo 'SSH connection successful'" 2>/dev/null; then
    echo "✅ SSH connection works"
else
    echo "❌ SSH connection failed"
    echo "   Please check:"
    echo "   1. SSH is enabled: Control Panel → Terminal & SNMP → Enable SSH"
    echo "   2. Username and password are correct"
    exit 1
fi

echo ""
echo "Step 3: Creating directory on NAS..."
$SSH_CMD ${NAS_USER}@${NAS_IP} "mkdir -p ${TARGET_DIR}/data ${TARGET_DIR}/exports" || {
    echo "❌ Failed to create directories"
    exit 1
}
echo "✅ Directories created"

echo ""
echo "Step 4: Copying files to NAS..."
echo "   This may take a minute..."

# Copy all necessary files
$SCP_CMD -r *.py ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true
$SCP_CMD -r templates ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true
$SCP_CMD requirements.txt Dockerfile docker-compose.yml .dockerignore ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true
$SCP_CMD synology_one_click.sh ${NAS_USER}@${NAS_IP}:${TARGET_DIR}/ 2>/dev/null || true

echo "✅ Files copied"

echo ""
echo "Step 5: Running deployment on NAS..."
echo "   (This will take 2-3 minutes to build Docker image)"

# Run deployment script on NAS
$SSH_CMD ${NAS_USER}@${NAS_IP} << 'ENDSSH'
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

