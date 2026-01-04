#!/bin/bash
# Verify complete setup - DNS, OAuth URLs, etc.

echo "🔍 Verifying Complete Setup"
echo "============================"
echo ""

# Check hosts file
echo "📋 Checking /etc/hosts..."
if grep -q "youtube-automation.local" /etc/hosts 2>/dev/null; then
    echo "✅ DNS entry found in /etc/hosts:"
    grep "youtube-automation.local" /etc/hosts
else
    echo "❌ DNS entry NOT found in /etc/hosts"
    echo "   Run: ./setup_local_dns_mac.sh"
fi

echo ""

# Test DNS resolution
echo "🧪 Testing DNS resolution..."
if ping -c 1 youtube-automation.local > /dev/null 2>&1; then
    echo "✅ DNS resolution works!"
    ping -c 1 youtube-automation.local | grep "PING"
else
    echo "❌ DNS resolution failed"
    echo "   Try: sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder"
fi

echo ""

# Check if Flask is running
echo "🚀 Checking Flask server..."
if curl -s http://youtube-automation.local:5001 > /dev/null 2>&1; then
    echo "✅ Flask server is running and accessible!"
    echo "   Access: http://youtube-automation.local:5001"
else
    echo "⚠️  Flask server not accessible"
    echo "   Start with: python3 run.py"
fi

echo ""

# Show OAuth URLs
echo "📋 OAuth Redirect URLs (Copy these to OAuth providers):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔵 GOOGLE:"
echo "   http://youtube-automation.local/oauth2callback"
echo ""
echo "🔵 LINKEDIN:"
echo "   http://youtube-automation.local:5001/api/linkedin/oauth/callback"
echo ""
echo "🔵 FACEBOOK/INSTAGRAM:"
echo "   http://youtube-automation.local:5001/api/facebook/oauth/callback"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check documentation files
echo "📚 Documentation files:"
if [ -f "COMPLETE_OAUTH_SETUP.md" ]; then
    echo "✅ COMPLETE_OAUTH_SETUP.md"
else
    echo "❌ COMPLETE_OAUTH_SETUP.md not found"
fi

if [ -f "SETUP_SUMMARY.md" ]; then
    echo "✅ SETUP_SUMMARY.md"
else
    echo "❌ SETUP_SUMMARY.md not found"
fi

if [ -f "OAUTH_REDIRECT_URLS.txt" ]; then
    echo "✅ OAUTH_REDIRECT_URLS.txt"
else
    echo "❌ OAUTH_REDIRECT_URLS.txt not found"
fi

echo ""
echo "✅ Setup verification complete!"
echo ""
echo "📖 See COMPLETE_OAUTH_SETUP.md for detailed OAuth configuration"

