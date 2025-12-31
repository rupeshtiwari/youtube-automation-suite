#!/bin/bash

# Setup Docker Permissions for Synology
# This script adds your user to the docker group

NAS_IP="192.168.68.108"
NAS_USER="rupesh"
NAS_PASSWORD="8xrBZyb6PuBFkqVfkgj6"

echo "🔐 Setting up Docker Permissions on Synology"
echo "============================================"
echo ""
echo "This will add user '${NAS_USER}' to the docker group"
echo "so you can run Docker commands without sudo."
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo ""
echo "Step 1: SSH into NAS as admin..."
echo "   (You'll need admin password)"

# SSH and add user to docker group
ssh ${NAS_USER}@${NAS_IP} << 'ENDSSH'
# Check if user is already in docker group
if groups | grep -q docker; then
    echo "✅ User is already in docker group"
else
    echo "Adding user to docker group..."
    # Try with sudo first
    if sudo synogroup --add docker $(whoami) 2>/dev/null; then
        echo "✅ Added to docker group"
    else
        echo "⚠️  Could not add to docker group automatically"
        echo ""
        echo "Please run manually:"
        echo "   sudo synogroup --add docker $(whoami)"
        echo ""
        echo "Or use admin account:"
        echo "   ssh admin@192.168.68.108"
        echo "   sudo synogroup --add docker rupesh"
    fi
fi

echo ""
echo "Current groups:"
groups
ENDSSH

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo ""
echo "⚠️  Important: You need to log out and back in"
echo "   for group changes to take effect."
echo ""
echo "After logging back in, test with:"
echo "   ssh ${NAS_USER}@${NAS_IP} 'docker ps'"
echo ""

