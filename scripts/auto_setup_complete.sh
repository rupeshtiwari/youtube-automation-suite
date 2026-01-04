#!/bin/bash
# Complete automatic setup - DNS, verification, everything!

set -e

DOMAIN="youtube-automation.local"
HOSTS_FILE="/etc/hosts"

echo "🚀 Complete Automatic Setup"
echo "============================"
echo ""

# Check if already configured
if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
    echo "✅ DNS entry already exists in /etc/hosts"
    grep "$DOMAIN" "$HOSTS_FILE"
else
    echo "📝 Adding DNS entry to /etc/hosts..."
    echo "   (You'll be prompted for your password)"
    echo ""
    
    # Add entry with sudo
    echo "127.0.0.1    $DOMAIN" | sudo tee -a "$HOSTS_FILE" > /dev/null
    
    if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
        echo "✅ Successfully added to /etc/hosts"
    else
        echo "❌ Failed to add to /etc/hosts"
        echo "   Please run manually: sudo nano /etc/hosts"
        echo "   Add: 127.0.0.1    $DOMAIN"
        exit 1
    fi
fi

echo ""

# Flush DNS cache
echo "🔄 Flushing DNS cache..."
sudo dscacheutil -flushcache 2>/dev/null || true
sudo killall -HUP mDNSResponder 2>/dev/null || true
echo "✅ DNS cache flushed"

echo ""

# Test DNS resolution
echo "🧪 Testing DNS resolution..."
sleep 1
if ping -c 1 "$DOMAIN" > /dev/null 2>&1; then
    echo "✅ DNS resolution works!"
    ping -c 1 "$DOMAIN" | grep "PING" | head -1
else
    echo "⚠️  DNS resolution test failed (might need a moment)"
    echo "   Try: ping $DOMAIN"
fi

echo ""

# Show OAuth URLs
echo "📋 OAuth Redirect URLs - Copy These:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔵 GOOGLE CLOUD CONSOLE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Authorized JavaScript origins:"
echo "  http://$DOMAIN"
echo "  http://$DOMAIN:5001"
echo ""
echo "Authorized redirect URIs:"
echo "  http://$DOMAIN/oauth2callback"
echo "  http://$DOMAIN:5001/oauth2callback"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔵 LINKEDIN DEVELOPER PORTAL:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Authorized redirect URLs:"
echo "  http://$DOMAIN:5001/api/linkedin/oauth/callback"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔵 FACEBOOK DEVELOPERS:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Valid OAuth Redirect URIs:"
echo "  http://$DOMAIN:5001/api/facebook/oauth/callback"
echo ""
echo "(Instagram uses the same URL)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check Flask
echo "🚀 Checking Flask server..."
if curl -s "http://$DOMAIN:5001" > /dev/null 2>&1; then
    echo "✅ Flask server is running!"
    echo "   Access: http://$DOMAIN:5001"
else
    echo "ℹ️  Flask server not running"
    echo "   Start with: python3 run.py"
fi

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📚 Documentation:"
echo "   - COMPLETE_OAUTH_SETUP.md (detailed guide)"
echo "   - OAUTH_REDIRECT_URLS.txt (quick reference)"
echo "   - SETUP_SUMMARY.md (overview)"
echo ""
echo "🧪 Verify setup: ./verify_setup.sh"
echo ""

