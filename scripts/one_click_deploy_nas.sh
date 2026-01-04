#!/bin/bash
# ONE-CLICK NAS DEPLOYMENT - For Synology DS224

set -e

DOMAIN="youtube-automation.local"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 ONE-CLICK NAS DEPLOYMENT"
echo "==========================="
echo ""
echo "This script prepares your project for Synology DS224 deployment"
echo ""
echo "⚠️  PREREQUISITES:"
echo "   1. Mac setup must be complete (run: ./one_click_setup_mac.sh)"
echo "   2. OAuth must be configured with youtube-automation.local domain"
echo "   3. You have SSH access to your Synology NAS"
echo ""

read -p "Continue with NAS deployment preparation? (y/n): " CONTINUE
if [ "$CONTINUE" != "y" ]; then
    echo "⏭️  Cancelled"
    exit 0
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Gathering NAS Information"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Enter your Synology NAS IP address (e.g., 192.168.1.100): " NAS_IP
if [ -z "$NAS_IP" ]; then
    echo "❌ NAS IP is required"
    exit 1
fi

read -p "Enter NAS username (default: admin): " NAS_USER
NAS_USER=${NAS_USER:-admin}

read -p "Enter deployment directory on NAS (default: /volume1/docker/youtube-automation): " NAS_DIR
NAS_DIR=${NAS_DIR:-/volume1/docker/youtube-automation}

echo ""
echo "✅ NAS Information:"
echo "   IP: $NAS_IP"
echo "   User: $NAS_USER"
echo "   Directory: $NAS_DIR"
echo ""

# Step 2: Create deployment package
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Creating Deployment Package"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Build React app if not already built
if [ ! -d "frontend/dist" ]; then
    echo "🔨 Building React app..."
    cd frontend && npm run build && cd ..
fi

# Create deployment archive (excluding unnecessary files)
echo "📦 Creating deployment package..."
tar -czf nas_deployment.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='frontend/node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='token.json' \
    --exclude='youtube_automation.db' \
    --exclude='nas_deployment.tar.gz' \
    app/ frontend/dist/ run.py requirements.txt \
    client_secret.json docker-compose.yml Dockerfile \
    *.md *.sh 2>/dev/null || {
    echo "⚠️  Some files may be missing, but continuing..."
}

echo "✅ Deployment package created: nas_deployment.tar.gz"
echo ""

# Step 3: Create NAS setup script
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Creating NAS Setup Instructions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat > NAS_DEPLOYMENT_INSTRUCTIONS.md << EOF
# One-Click NAS Deployment Instructions

## 📋 Deployment Information

- **Domain:** $DOMAIN
- **NAS IP:** $NAS_IP
- **NAS User:** $NAS_USER
- **Deployment Directory:** $NAS_DIR

## 🚀 Quick Deployment Steps

### Step 1: Transfer Files to NAS

**Option A: Using SCP (from Mac terminal):**
\`\`\`bash
scp nas_deployment.tar.gz $NAS_USER@$NAS_IP:$NAS_DIR/
\`\`\`

**Option B: Using Synology File Station:**
1. Open File Station on NAS
2. Navigate to $NAS_DIR
3. Upload \`nas_deployment.tar.gz\`

### Step 2: SSH into NAS

\`\`\`bash
ssh $NAS_USER@$NAS_IP
\`\`\`

### Step 3: Extract and Setup

\`\`\`bash
cd $NAS_DIR
tar -xzf nas_deployment.tar.gz

# Install Python dependencies
python3 -m pip install -r requirements.txt

# Build React app (if not included)
cd frontend && npm install && npm run build && cd ..
\`\`\`

### Step 4: Configure DNS Server on Synology

1. **Open Package Center** on Synology DSM
2. **Install "DNS Server"** package
3. **Open DNS Server** application
4. **Create Zone:**
   - Go to "Zones" tab
   - Click "Create" → "Master zone"
   - Zone name: \`local\`
   - Click "Next" → "Next" → "Apply"
5. **Add A Record:**
   - Select \`local\` zone
   - Click "Create" → "A Record"
   - Hostname: \`youtube-automation\`
   - IPv4 Address: \`$NAS_IP\`
   - Click "OK"

### Step 5: Run Application

\`\`\`bash
cd $NAS_DIR
python3 run.py
\`\`\`

Or use systemd service (see below).

### Step 6: Access Application

- **Local network:** http://$DOMAIN:5001
- **From any device on network** (if router DNS configured)

## 🔧 Optional: Systemd Service (Auto-start)

Create \`/etc/systemd/system/youtube-automation.service\`:

\`\`\`ini
[Unit]
Description=YouTube Automation App
After=network.target

[Service]
Type=simple
User=$NAS_USER
WorkingDirectory=$NAS_DIR
ExecStart=/usr/bin/python3 $NAS_DIR/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
\`\`\`

Enable and start:
\`\`\`bash
sudo systemctl enable youtube-automation
sudo systemctl start youtube-automation
\`\`\`

## ✅ OAuth Configuration

**No changes needed!** OAuth is already configured with:
- Domain: $DOMAIN
- Redirect URLs work on NAS (via DNS Server)

Just make sure DNS Server is set up (Step 4).

## 🧪 Verification

1. **Test DNS:**
   \`\`\`bash
   nslookup $DOMAIN
   # Should return: $NAS_IP
   \`\`\`

2. **Test App:**
   - Open: http://$DOMAIN:5001
   - Should load your app

3. **Test OAuth:**
   - Try connecting LinkedIn/Facebook
   - Should work with same redirect URLs

## 📚 Additional Resources

- See \`DS224_SYNOLOGY_DNS.md\` for detailed DNS setup
- See \`COMPLETE_OAUTH_SETUP.md\` for OAuth details
- See \`DEPLOY_NAS.md\` for general NAS deployment

## 🎯 Summary

1. ✅ Transfer \`nas_deployment.tar.gz\` to NAS
2. ✅ Extract and install dependencies
3. ✅ Set up DNS Server (zone: local, A record: youtube-automation → $NAS_IP)
4. ✅ Run: \`python3 run.py\`
5. ✅ Access: http://$DOMAIN:5001

**Same OAuth config works - no changes needed!** 🎉
EOF

echo "✅ NAS deployment instructions created: NAS_DEPLOYMENT_INSTRUCTIONS.md"
echo ""

# Step 4: Create automated deployment script
cat > deploy_to_nas.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
# Automated deployment to NAS

set -e

if [ -z "$1" ]; then
    echo "Usage: ./deploy_to_nas.sh <NAS_IP> [NAS_USER] [NAS_DIR]"
    echo "Example: ./deploy_to_nas.sh 192.168.1.100 admin /volume1/docker/youtube-automation"
    exit 1
fi

NAS_IP=$1
NAS_USER=${2:-admin}
NAS_DIR=${3:-/volume1/docker/youtube-automation}

echo "🚀 Deploying to NAS..."
echo "   IP: $NAS_IP"
echo "   User: $NAS_USER"
echo "   Directory: $NAS_DIR"
echo ""

# Check if deployment package exists
if [ ! -f "nas_deployment.tar.gz" ]; then
    echo "❌ nas_deployment.tar.gz not found"
    echo "   Run: ./one_click_deploy_nas.sh first"
    exit 1
fi

# Transfer to NAS
echo "📤 Transferring files to NAS..."
scp nas_deployment.tar.gz "$NAS_USER@$NAS_IP:$NAS_DIR/"

# SSH and extract
echo "📦 Extracting on NAS..."
ssh "$NAS_USER@$NAS_IP" << SSH_CMD
cd $NAS_DIR
tar -xzf nas_deployment.tar.gz
python3 -m pip install -r requirements.txt --user
echo "✅ Files extracted and dependencies installed"
SSH_CMD

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Next steps:"
echo "1. SSH into NAS: ssh $NAS_USER@$NAS_IP"
echo "2. Set up DNS Server (see NAS_DEPLOYMENT_INSTRUCTIONS.md)"
echo "3. Run: cd $NAS_DIR && python3 run.py"
echo "4. Access: http://youtube-automation.local:5001"
echo ""
DEPLOY_SCRIPT

chmod +x deploy_to_nas.sh
echo "✅ Automated deployment script created: deploy_to_nas.sh"
echo ""

# Step 5: Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 4: Deployment Package Ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Created files:"
echo "   - nas_deployment.tar.gz (deployment package)"
echo "   - NAS_DEPLOYMENT_INSTRUCTIONS.md (step-by-step guide)"
echo "   - deploy_to_nas.sh (automated deployment script)"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "Option 1: Automated (recommended):"
echo "   ./deploy_to_nas.sh $NAS_IP $NAS_USER $NAS_DIR"
echo ""
echo "Option 2: Manual:"
echo "   1. Transfer nas_deployment.tar.gz to NAS"
echo "   2. Follow NAS_DEPLOYMENT_INSTRUCTIONS.md"
echo ""
echo "📚 See NAS_DEPLOYMENT_INSTRUCTIONS.md for complete guide"
echo ""
echo "✅ NAS deployment preparation complete!"
echo ""

