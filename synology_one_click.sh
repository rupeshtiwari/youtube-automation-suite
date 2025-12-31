#!/bin/bash

# Synology One-Click Deployment Script
# This script automates the entire deployment process

set -e

echo "🚀 YouTube Automation - Synology One-Click Deployment"
echo "===================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="youtube-automation"
APP_DIR="/volume1/docker/${APP_NAME}"
DATA_DIR="/volume1/docker/${APP_NAME}/data"
EXPORTS_DIR="/volume1/docker/${APP_NAME}/exports"

echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"

# Check if Docker is installed (try with sudo if needed)
if command -v docker &> /dev/null; then
    DOCKER_CMD="docker"
    echo -e "${GREEN}✅ Docker found${NC}"
elif sudo -n docker --version &> /dev/null 2>&1; then
    DOCKER_CMD="sudo docker"
    echo -e "${GREEN}✅ Docker found (requires sudo)${NC}"
else
    echo -e "${RED}❌ Docker not found!${NC}"
    echo "Please install Docker from Package Center first."
    echo ""
    echo "Note: On Synology, you may need to:"
    echo "1. Add your user to 'docker' group, OR"
    echo "2. Use sudo for Docker commands"
    exit 1
fi

# Check if Docker Compose is available (try with sudo if needed)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
    echo -e "${GREEN}✅ docker-compose found${NC}"
elif sudo -n docker-compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="sudo docker-compose"
    echo -e "${GREEN}✅ docker-compose found (requires sudo)${NC}"
elif $DOCKER_CMD compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="$DOCKER_CMD compose"
    echo -e "${GREEN}✅ Using 'docker compose' (newer syntax)${NC}"
elif sudo -n docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE="sudo docker compose"
    echo -e "${GREEN}✅ Using 'sudo docker compose' (newer syntax)${NC}"
else
    echo -e "${RED}❌ docker-compose not available${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 2: Creating directories...${NC}"

# Create directories
mkdir -p "${APP_DIR}"
mkdir -p "${DATA_DIR}"
mkdir -p "${EXPORTS_DIR}"

echo -e "${GREEN}✅ Directories created${NC}"
echo "   - App: ${APP_DIR}"
echo "   - Data: ${DATA_DIR}"
echo "   - Exports: ${EXPORTS_DIR}"

echo ""
echo -e "${BLUE}Step 3: Checking for required files...${NC}"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found!${NC}"
    echo "Please run this script from the project directory."
    exit 1
fi

# Check for client_secret.json
if [ ! -f "client_secret.json" ]; then
    echo -e "${YELLOW}⚠️  client_secret.json not found${NC}"
    echo "   You'll need to add this file after deployment."
    echo "   Place it in: ${APP_DIR}/client_secret.json"
else
    echo -e "${GREEN}✅ client_secret.json found${NC}"
fi

# Check for .env
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    echo "   Creating template .env file..."
    cat > "${APP_DIR}/.env" << EOF
# YouTube Automation Environment Variables
# Add your API keys here

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=

# Facebook Graph API
FACEBOOK_PAGE_ACCESS_TOKEN=
FACEBOOK_PAGE_ID=

# Instagram Graph API
INSTAGRAM_BUSINESS_ACCOUNT_ID=
INSTAGRAM_ACCESS_TOKEN=

# Ayrshare (Alternative)
AYRSHARE_API_KEY=

# YouTube Playlist ID
YOUTUBE_PLAYLIST_ID=

# Security
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo -e "${GREEN}✅ Template .env created${NC}"
    echo "   Edit: ${APP_DIR}/.env"
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Copying files to NAS location...${NC}"

# Copy all necessary files
cp -r *.py "${APP_DIR}/" 2>/dev/null || true
cp -r templates "${APP_DIR}/" 2>/dev/null || true
cp requirements.txt "${APP_DIR}/" 2>/dev/null || true
cp Dockerfile "${APP_DIR}/" 2>/dev/null || true
cp docker-compose.yml "${APP_DIR}/" 2>/dev/null || true
cp .dockerignore "${APP_DIR}/" 2>/dev/null || true

# Copy credentials if they exist
[ -f "client_secret.json" ] && cp client_secret.json "${APP_DIR}/" || true
[ -f ".env" ] && cp .env "${APP_DIR}/" || true

echo -e "${GREEN}✅ Files copied${NC}"

echo ""
echo -e "${BLUE}Step 5: Building Docker image...${NC}"

cd "${APP_DIR}"

# Build the image
if docker build -t ${APP_NAME}:latest .; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Step 6: Starting container...${NC}"

# Stop existing container if running
if $DOCKER_CMD ps -a | grep -q ${APP_NAME}; then
    echo "Stopping existing container..."
    ${DOCKER_COMPOSE} down 2>/dev/null || $DOCKER_CMD stop ${APP_NAME} 2>/dev/null || true
fi

# Start new container
if ${DOCKER_COMPOSE} up -d; then
    echo -e "${GREEN}✅ Container started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start container${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
$DOCKER_CMD ps | grep ${APP_NAME} || echo "Container not running"

echo ""
echo -e "${BLUE}🌐 Access your application:${NC}"
echo "   Local: http://$(hostname -I | awk '{print $1}'):5000"
echo "   Or: http://localhost:5000"
echo ""

# Get container IP
CONTAINER_IP=$($DOCKER_CMD inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ${APP_NAME} 2>/dev/null || echo "N/A")
if [ "$CONTAINER_IP" != "N/A" ]; then
    echo -e "${BLUE}   Container IP: ${CONTAINER_IP}:5000${NC}"
fi

echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo "   View logs:    cd ${APP_DIR} && ${DOCKER_COMPOSE} logs -f"
echo "   Stop:         cd ${APP_DIR} && ${DOCKER_COMPOSE} down"
echo "   Restart:      cd ${APP_DIR} && ${DOCKER_COMPOSE} restart"
echo "   Update:       cd ${APP_DIR} && git pull && ${DOCKER_COMPOSE} up -d --build"
echo ""

echo -e "${BLUE}📁 Important Files:${NC}"
echo "   App Directory: ${APP_DIR}"
echo "   Database:      ${DATA_DIR}/youtube_automation.db"
echo "   Settings:      ${DATA_DIR}/automation_settings.json"
echo "   Exports:       ${EXPORTS_DIR}/"
echo ""

echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "   1. Open http://localhost:5000 in your browser"
echo "   2. Configure API keys in the web interface"
echo "   3. Set up your automation schedule"
echo ""

echo -e "${GREEN}🎉 Enjoy your automated YouTube workflow!${NC}"

