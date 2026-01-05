#!/bin/bash

# RootitVPN - Automated Installation Script
# For Ubuntu 22.04 LTS
# Usage: bash install.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "=========================================="
echo "  RootitVPN - Automated Installation"
echo "  VPN Management Panel for Xray-core"
echo "=========================================="
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Detect OS
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}❌ Cannot detect OS${NC}"
    exit 1
fi

. /etc/os-release
OS=$ID
VER=$VERSION_ID

echo -e "${YELLOW}📦 Detected OS: $OS $VER${NC}"

# Step 1: Update system
echo -e "\n${BLUE}[1/8]${NC} ${YELLOW}Updating system packages...${NC}"
apt-get update -qq
apt-get install -y -qq curl wget git unzip > /dev/null 2>&1
echo -e "${GREEN}✓ System updated${NC}"

# Step 2: Install Docker
echo -e "\n${BLUE}[2/8]${NC} ${YELLOW}Installing Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker already installed${NC}"
else
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
fi

# Step 3: Install Docker Compose
echo -e "\n${BLUE}[3/8]${NC} ${YELLOW}Installing Docker Compose...${NC}"
if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
else
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
fi

# Step 4: Clone or update repository
echo -e "\n${BLUE}[4/8]${NC} ${YELLOW}Setting up project...${NC}"
INSTALL_DIR="/opt/rootitvpn"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠ Directory exists, updating...${NC}"
    cd "$INSTALL_DIR"
    git pull > /dev/null 2>&1 || echo -e "${YELLOW}⚠ Could not update, using existing files${NC}"
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    git clone https://github.com/rootitazam/rootitvpn.git "$INSTALL_DIR" > /dev/null 2>&1
    cd "$INSTALL_DIR"
fi
echo -e "${GREEN}✓ Project ready${NC}"

# Step 5: Setup environment
echo -e "\n${BLUE}[5/8]${NC} ${YELLOW}Setting up environment...${NC}"
if [ ! -f .env ]; then
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me || curl -s ipinfo.io/ip || echo "")
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Create .env file
    cat > .env << EOF
# Backend Configuration
SECRET_KEY=${SECRET_KEY}
DATABASE_URL=sqlite:///./data/rootitvpn.db
XRAY_GRPC_ADDRESS=xray:8080

# Admin Credentials (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-16)

# Server IP
SERVER_IP=${SERVER_IP}

# Frontend Configuration
VITE_API_URL=http://${SERVER_IP}:8000

# Xray Configuration
XRAY_PORT=443
XRAY_GRPC_PORT=8080

# Reality Settings
REALITY_DEST=www.microsoft.com:443
REALITY_SERVER_NAMES=www.microsoft.com,www.cloudflare.com,www.github.com

# Log Rotation
LOG_RETENTION_HOURS=24
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ IMPORTANT: Admin password saved in .env file${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Step 6: Download GeoIP/Geosite
echo -e "\n${BLUE}[6/8]${NC} ${YELLOW}Downloading GeoIP/Geosite files...${NC}"
mkdir -p xray/geoip xray/geosite
if [ ! -f xray/geoip/geoip.dat ] || [ ! -f xray/geosite/geosite.dat ]; then
    chmod +x xray/download-geo.sh
    ./xray/download-geo.sh > /dev/null 2>&1
    echo -e "${GREEN}✓ GeoIP/Geosite files downloaded${NC}"
else
    echo -e "${GREEN}✓ GeoIP/Geosite files already exist${NC}"
fi

# Step 7: Create directories and config
echo -e "\n${BLUE}[7/8]${NC} ${YELLOW}Creating directories and config...${NC}"
mkdir -p xray/config xray/logs backend/data
if [ ! -f xray/config/config.json ]; then
    cp xray/config.json.template xray/config/config.json
    echo -e "${GREEN}✓ Xray config created${NC}"
else
    echo -e "${GREEN}✓ Xray config already exists${NC}"
fi

# Step 8: Start services
echo -e "\n${BLUE}[8/8]${NC} ${YELLOW}Starting services with Docker Compose...${NC}"
docker-compose down > /dev/null 2>&1 || true

# Build images first
echo -e "${YELLOW}Building Docker images (this may take a few minutes)...${NC}"
docker-compose build --no-cache

# Start services
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"

# Wait for services to be ready
echo -e "\n${YELLOW}⏳ Waiting for services to start (30 seconds)...${NC}"
sleep 30

# Check services status
echo -e "\n${BLUE}📊 Service Status:${NC}"
docker-compose ps

# Check if Xray is healthy, if not show logs
XRAY_STATUS=$(docker-compose ps xray | grep -o "unhealthy\|healthy\|starting" | head -1)
if [ "$XRAY_STATUS" != "healthy" ]; then
    echo -e "\n${YELLOW}⚠ Xray container is not healthy. Checking logs...${NC}"
    echo -e "${BLUE}Xray logs (last 20 lines):${NC}"
    docker-compose logs --tail=20 xray
    echo -e "\n${YELLOW}⚠ If Xray is failing, you may need to check the config.json file${NC}"
    echo -e "${YELLOW}⚠ The backend and frontend should still work${NC}"
fi

# Get admin password from .env
ADMIN_PASSWORD=$(grep "ADMIN_PASSWORD=" .env | cut -d'=' -f2)
SERVER_IP=$(grep "SERVER_IP=" .env | cut -d'=' -f2)

# Final message
echo -e "\n${GREEN}"
echo "=========================================="
echo "  ✅ Installation Complete!"
echo "=========================================="
echo -e "${NC}"
echo -e "${BLUE}📱 Access Information:${NC}"
echo -e "  Frontend:  ${GREEN}http://${SERVER_IP}:3000${NC}"
echo -e "  Backend:   ${GREEN}http://${SERVER_IP}:8000${NC}"
echo -e "  API Docs:  ${GREEN}http://${SERVER_IP}:8000/docs${NC}"
echo ""
echo -e "${BLUE}🔐 Admin Credentials:${NC}"
echo -e "  Username: ${GREEN}admin${NC}"
echo -e "  Password: ${GREEN}${ADMIN_PASSWORD}${NC}"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT:${NC}"
echo -e "  1. Change admin password after first login"
echo -e "  2. Configure Server IP in Settings panel if needed"
echo -e "  3. Open firewall ports: 3000, 8000, 443, 8080"
echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "  View logs:    ${GREEN}docker-compose logs -f${NC}"
echo -e "  Restart:      ${GREEN}docker-compose restart${NC}"
echo -e "  Stop:         ${GREEN}docker-compose down${NC}"
echo -e "  Status:       ${GREEN}docker-compose ps${NC}"
echo ""

