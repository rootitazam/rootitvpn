#!/bin/bash

# RootitVPN - Xray-core Installation Script
# For Ubuntu 22.04 LTS

set -e

echo "=========================================="
echo "RootitVPN - Xray-core Installation"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        ARCH="64"
        ;;
    aarch64|arm64)
        ARCH="arm64-v8a"
        ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}Detected architecture: $ARCH${NC}"

# Get latest Xray version
echo -e "${YELLOW}Fetching latest Xray version...${NC}"
LATEST_VERSION=$(curl -s https://api.github.com/repos/XTLS/Xray-core/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_VERSION" ]; then
    echo -e "${RED}Failed to fetch latest version${NC}"
    exit 1
fi

echo -e "${GREEN}Latest version: $LATEST_VERSION${NC}"

# Download Xray
DOWNLOAD_URL="https://github.com/XTLS/Xray-core/releases/download/${LATEST_VERSION}/Xray-linux-${ARCH}.zip"
TMP_DIR=$(mktemp -d)
XRAY_FILE="$TMP_DIR/xray.zip"

echo -e "${YELLOW}Downloading Xray...${NC}"
wget -q -O "$XRAY_FILE" "$DOWNLOAD_URL" || {
    echo -e "${RED}Failed to download Xray${NC}"
    exit 1
}

# Install unzip if not present
if ! command -v unzip &> /dev/null; then
    echo -e "${YELLOW}Installing unzip...${NC}"
    apt-get update -qq
    apt-get install -y unzip
fi

# Extract and install
echo -e "${YELLOW}Installing Xray...${NC}"
unzip -q "$XRAY_FILE" -d "$TMP_DIR"
mv "$TMP_DIR/xray" /usr/local/bin/xray
chmod +x /usr/local/bin/xray

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p /etc/xray
mkdir -p /var/log/xray
mkdir -p /usr/local/share/xray

# Download geoip and geosite files
echo -e "${YELLOW}Downloading geoip and geosite files...${NC}"
wget -q -O /usr/local/share/xray/geoip.dat https://github.com/v2fly/geoip/releases/latest/download/geoip.dat
wget -q -O /usr/local/share/xray/geosite.dat https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat

# Create systemd service
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/xray.service <<EOF
[Unit]
Description=Xray Service
Documentation=https://github.com/xtls
After=network.target nss-lookup.target

[Service]
User=nobody
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/xray run -config /etc/xray/config.json
Restart=on-failure
RestartPreventExitStatus=23
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

# Set permissions
chown -R nobody:nogroup /var/log/xray
chown -R nobody:nogroup /etc/xray

# Reload systemd
systemctl daemon-reload

# Enable Xray service
systemctl enable xray

echo -e "${GREEN}=========================================="
echo "Xray-core installed successfully!"
echo "==========================================${NC}"
echo ""
echo "Installation details:"
echo "  - Binary: /usr/local/bin/xray"
echo "  - Config: /etc/xray/config.json"
echo "  - Logs: /var/log/xray/"
echo "  - Service: xray.service"
echo ""
echo "Next steps:"
echo "  1. Copy config.json.template to /etc/xray/config.json"
echo "  2. Configure Reality settings"
echo "  3. Start service: systemctl start xray"
echo "  4. Check status: systemctl status xray"
echo ""

# Cleanup
rm -rf "$TMP_DIR"

echo -e "${GREEN}Installation completed!${NC}"

