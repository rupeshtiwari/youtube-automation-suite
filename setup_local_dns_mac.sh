#!/bin/bash
# Setup local DNS for Mac development
# Adds youtube-automation.local to /etc/hosts

set -e

DOMAIN="youtube-automation.local"
HOSTS_FILE="/etc/hosts"

echo "🔧 Local DNS Setup for Mac"
echo "=========================="
echo ""

# Check if domain already exists
if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
    echo "✅ Domain already configured in $HOSTS_FILE:"
    grep "$DOMAIN" "$HOSTS_FILE"
    echo ""
    read -p "Update it? (y/n): " UPDATE
    if [ "$UPDATE" != "y" ]; then
        echo "⏭️  Skipped. Using existing configuration."
        exit 0
    fi
    # Remove old entry
    sudo sed -i '' "/$DOMAIN/d" "$HOSTS_FILE"
fi

echo "🔐 Adding $DOMAIN → 127.0.0.1 to $HOSTS_FILE"
echo "   (Requires sudo password)"
echo ""

# Add entry
echo "127.0.0.1    $DOMAIN" | sudo tee -a "$HOSTS_FILE" > /dev/null

echo "✅ Added successfully!"
echo ""

# Test
echo "🧪 Testing DNS resolution..."
if ping -c 1 "$DOMAIN" > /dev/null 2>&1; then
    echo "✅ DNS resolution works!"
    echo "   $DOMAIN → 127.0.0.1"
else
    echo "⚠️  DNS resolution test failed (might need to flush DNS cache)"
    echo "   Try: sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder"
fi

echo ""
echo "📋 Google OAuth Configuration:"
echo "=============================="
echo ""
echo "Authorized JavaScript origins:"
echo "  http://$DOMAIN"
echo "  http://$DOMAIN:5001"
echo ""
echo "Authorized redirect URIs:"
echo "  http://$DOMAIN/oauth2callback"
echo "  http://$DOMAIN:5001/oauth2callback"
echo ""
echo "⚠️  IMPORTANT: Update Google Cloud Console OAuth Client with these URIs!"
echo ""
echo "🚀 Access your app at:"
echo "   http://$DOMAIN:5001"
echo ""
echo "✅ Mac setup complete!"
echo ""
echo "📚 Next: When deploying to DS224 NAS, set up DNS Server to resolve"
echo "   $DOMAIN → Your NAS IP"
echo "   See LOCAL_DNS_SETUP.md for DS224 instructions"

