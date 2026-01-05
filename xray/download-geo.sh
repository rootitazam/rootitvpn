#!/bin/bash

# Download GeoIP and Geosite files for Xray
# These files are required for routing rules (geoip:ir, geosite:ir, etc.)

set -e

GEOIP_URL="https://github.com/v2fly/geoip/releases/latest/download/geoip.dat"
GEOSITE_URL="https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat"

GEOIP_DIR="./xray/geoip"
GEOSITE_DIR="./xray/geosite"

# Create directories
mkdir -p "$GEOIP_DIR"
mkdir -p "$GEOSITE_DIR"

echo "Downloading GeoIP file..."
wget -q -O "$GEOIP_DIR/geoip.dat" "$GEOIP_URL" || {
    echo "Error: Failed to download geoip.dat"
    exit 1
}

echo "Downloading Geosite file..."
wget -q -O "$GEOSITE_DIR/geosite.dat" "$GEOSITE_URL" || {
    echo "Error: Failed to download geosite.dat"
    exit 1
}

echo "GeoIP and Geosite files downloaded successfully!"
echo "GeoIP: $GEOIP_DIR/geoip.dat"
echo "Geosite: $GEOSITE_DIR/geosite.dat"

