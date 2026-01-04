#!/bin/bash
# Setup script for domain-based OAuth (long-term solution)
# This makes OAuth work both locally and on NAS without changing redirect URIs

set -e

echo "🔧 Domain-Based OAuth Setup"
echo "============================"
echo ""

# Ask for domain
read -p "Enter your domain (e.g., youtube-automation.duckdns.org): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ Domain is required!"
    exit 1
fi

echo ""
echo "📝 Domain: $DOMAIN"
echo ""

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    HOSTS_FILE="/etc/hosts"
    echo "🖥️  Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    HOSTS_FILE="/etc/hosts"
    echo "🖥️  Detected Linux"
else
    echo "❌ Unsupported OS. Please manually edit hosts file."
    exit 1
fi

echo ""
echo "📋 Google Cloud Console OAuth Configuration:"
echo "=============================================="
echo ""
echo "Authorized JavaScript origins:"
echo "  http://$DOMAIN"
echo "  https://$DOMAIN"
echo ""
echo "Authorized redirect URIs:"
echo "  http://$DOMAIN/oauth2callback"
echo "  https://$DOMAIN/oauth2callback"
echo ""
echo "⚠️  IMPORTANT: Update your Google Cloud Console OAuth Client with these URIs!"
echo ""

# Check if domain already in hosts file
if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
    echo "✅ Domain already in $HOSTS_FILE"
    grep "$DOMAIN" "$HOSTS_FILE"
else
    echo ""
    read -p "Add $DOMAIN to $HOSTS_FILE for local development? (y/n): " ADD_HOSTS
    
    if [ "$ADD_HOSTS" = "y" ]; then
        echo ""
        echo "🔐 Requires sudo password to edit $HOSTS_FILE"
        echo "127.0.0.1    $DOMAIN" | sudo tee -a "$HOSTS_FILE" > /dev/null
        echo "✅ Added $DOMAIN → 127.0.0.1 to $HOSTS_FILE"
        echo ""
        echo "Now you can access your app at: http://$DOMAIN:5001"
    else
        echo "⏭️  Skipped hosts file update. You can add it manually later."
        echo "   Add this line to $HOSTS_FILE:"
        echo "   127.0.0.1    $DOMAIN"
    fi
fi

echo ""
echo "🌐 For NAS Deployment:"
echo "======================"
echo ""
echo "1. Point DNS to your NAS IP:"
echo "   - DuckDNS: Update via web interface or client"
echo "   - Real domain: Add A record: $DOMAIN → YOUR_NAS_IP"
echo ""
echo "2. Deploy app to NAS (same code, no OAuth changes!)"
echo ""
echo "3. Access at: http://$DOMAIN:5001 (or https://$DOMAIN with reverse proxy)"
echo ""

# Create .env.example entry
echo ""
echo "📄 Creating .env.example entry..."
cat >> .env.example << EOF

# OAuth Redirect Base (optional - for custom domain setup)
# If set, OAuth will use this base URL. If not set, uses request hostname.
# Example: OAUTH_REDIRECT_BASE="https://youtube-automation.duckdns.org"
# OAUTH_REDIRECT_BASE=""
EOF

echo "✅ Setup complete!"
echo ""
echo "📚 Next Steps:"
echo "1. Update Google Cloud Console OAuth Client with the URIs above"
echo "2. Test locally: http://$DOMAIN:5001"
echo "3. When deploying to NAS, point DNS to NAS IP"
echo "4. Same OAuth config works everywhere! 🎉"

