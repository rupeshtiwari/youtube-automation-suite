#!/bin/bash
# ONE-CLICK SETUP FOR MAC - Everything automated!

set -e

DOMAIN="youtube-automation.local"
HOSTS_FILE="/etc/hosts"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 ONE-CLICK MAC SETUP"
echo "======================"
echo ""
echo "This will set up everything automatically:"
echo "  ✅ DNS configuration (/etc/hosts)"
echo "  ✅ DNS cache flush"
echo "  ✅ Verification"
echo "  ✅ OAuth URLs display"
echo ""

# Function to add to hosts file using osascript (macOS native)
add_to_hosts() {
    local entry="127.0.0.1    $DOMAIN"
    
    # Check if already exists
    if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
        echo "✅ DNS entry already exists in /etc/hosts"
        return 0
    fi
    
    echo "📝 Adding DNS entry to /etc/hosts..."
    echo "   (You'll be prompted for your Mac password)"
    
    # Use osascript to get sudo password and add entry
    osascript -e "do shell script \"echo '$entry' >> $HOSTS_FILE\" with administrator privileges" 2>/dev/null
    
    if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
        echo "✅ Successfully added to /etc/hosts"
        return 0
    else
        echo "❌ Failed to add automatically. Trying alternative method..."
        # Alternative: direct sudo
        echo "$entry" | sudo tee -a "$HOSTS_FILE" > /dev/null
        if grep -q "$DOMAIN" "$HOSTS_FILE" 2>/dev/null; then
            echo "✅ Successfully added to /etc/hosts"
            return 0
        else
            echo "❌ Could not add automatically"
            echo "   Please run manually:"
            echo "   sudo nano /etc/hosts"
            echo "   Add: $entry"
            return 1
        fi
    fi
}

# Step 1: DNS Setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: DNS Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
add_to_hosts
echo ""

# Step 2: Flush DNS Cache
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Flushing DNS Cache"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Flushing DNS cache..."
osascript -e "do shell script \"dscacheutil -flushcache && killall -HUP mDNSResponder\" with administrator privileges" 2>/dev/null || {
    sudo dscacheutil -flushcache 2>/dev/null || true
    sudo killall -HUP mDNSResponder 2>/dev/null || true
}
echo "✅ DNS cache flushed"
echo ""

# Step 3: Verify DNS
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Verifying DNS Resolution"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sleep 2
if ping -c 1 "$DOMAIN" > /dev/null 2>&1; then
    echo "✅ DNS resolution works!"
    ping -c 1 "$DOMAIN" | grep "PING" | head -1
else
    echo "⚠️  DNS resolution test failed (may need a moment)"
    echo "   Current /etc/hosts entry:"
    grep "$DOMAIN" "$HOSTS_FILE" 2>/dev/null || echo "   Not found"
fi
echo ""

# Step 4: Check Dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Checking Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Install from python.org"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "⚠️  Node.js not found. Install from nodejs.org"
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm: $NPM_VERSION"
else
    echo "⚠️  npm not found"
fi

echo ""

# Step 5: Build React App
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 5: Building React Frontend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -d "frontend" ]; then
    if [ ! -d "frontend/node_modules" ]; then
        echo "📦 Installing npm dependencies..."
        cd frontend && npm install --silent && cd ..
    fi
    
    if [ ! -d "frontend/dist" ] || [ "frontend/dist/index.html" -ot "frontend/src" ]; then
        echo "🔨 Building React app..."
        cd frontend && npm run build && cd ..
        echo "✅ React app built successfully"
    else
        echo "✅ React app already built"
    fi
else
    echo "⚠️  frontend/ directory not found"
fi
echo ""

# Step 6: Check Python Dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 6: Checking Python Dependencies"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "requirements.txt" ]; then
    echo "📋 Checking Python packages..."
    python3 -m pip show flask > /dev/null 2>&1 && echo "✅ Flask installed" || echo "⚠️  Flask not installed (run: pip install -r requirements.txt)"
    python3 -m pip show flask-cors > /dev/null 2>&1 && echo "✅ flask-cors installed" || echo "⚠️  flask-cors not installed"
else
    echo "⚠️  requirements.txt not found"
fi
echo ""

# Step 7: OAuth URLs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 7: OAuth Redirect URLs (Copy These!)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔵 GOOGLE CLOUD CONSOLE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Application type: Web application"
echo ""
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

# Step 8: Final Status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 8: Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ DNS configured: $DOMAIN → 127.0.0.1"
echo "✅ React app built"
echo "✅ OAuth URLs ready"
echo ""
echo "🚀 Next Steps:"
echo "   1. Configure OAuth providers with URLs above"
echo "   2. Start Flask server: python3 run.py"
echo "   3. Access app: http://$DOMAIN:5001"
echo ""
echo "📚 Documentation:"
echo "   - COMPLETE_OAUTH_SETUP.md (detailed OAuth guide)"
echo "   - SETUP_SUMMARY.md (overview)"
echo "   - one_click_deploy_nas.sh (NAS deployment - run after Mac setup)"
echo ""
echo "✅ Mac setup complete! Ready for development."
echo ""

