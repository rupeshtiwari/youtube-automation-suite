#!/bin/bash

# Test NAS Connection Script
# This will verify everything is ready for deployment

NAS_IP="192.168.68.108"
NAS_USER="rupesh"

echo "🔍 Testing NAS Connection..."
echo "============================"
echo ""

# Test 1: Ping
echo "Test 1: Can we reach the NAS?"
if ping -c 3 -W 1 $NAS_IP &> /dev/null; then
    echo "✅ NAS is reachable at $NAS_IP"
    PING_OK=true
else
    echo "❌ Cannot reach NAS at $NAS_IP"
    echo "   Check: Are you on the same network?"
    PING_OK=false
fi
echo ""

# Test 2: SSH
echo "Test 2: Can we SSH into NAS?"
echo "   (You'll be prompted for password: 8xrBZyb6PuBFkqVfkgj6)"
if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ${NAS_USER}@${NAS_IP} "echo 'SSH test successful'" 2>/dev/null; then
    echo "✅ SSH connection works!"
    SSH_OK=true
else
    echo "❌ SSH connection failed"
    echo "   Check:"
    echo "   1. SSH is enabled: Control Panel → Terminal & SNMP"
    echo "   2. Username is correct: $NAS_USER"
    echo "   3. Password is correct"
    SSH_OK=false
fi
echo ""

# Test 3: Docker
echo "Test 3: Is Docker installed on NAS?"
if ssh -o ConnectTimeout=5 ${NAS_USER}@${NAS_IP} "docker --version" 2>/dev/null; then
    echo "✅ Docker is installed"
    DOCKER_OK=true
else
    echo "❌ Docker not found or not accessible"
    echo "   Install from: Package Center → Docker"
    DOCKER_OK=false
fi
echo ""

# Summary
echo "============================"
echo "📊 Test Results Summary:"
echo "   Ping:     $([ "$PING_OK" = true ] && echo "✅" || echo "❌")"
echo "   SSH:      $([ "$SSH_OK" = true ] && echo "✅" || echo "❌")"
echo "   Docker:   $([ "$DOCKER_OK" = true ] && echo "✅" || echo "❌")"
echo ""

if [ "$PING_OK" = true ] && [ "$SSH_OK" = true ] && [ "$DOCKER_OK" = true ]; then
    echo "🎉 All tests passed! Ready to deploy!"
    echo ""
    echo "Run deployment:"
    echo "   ./deploy_to_your_nas.sh"
else
    echo "⚠️  Some tests failed. Please fix the issues above first."
fi
echo ""

