#!/usr/bin/env bash
################################################################################
# UAV Master Hub - Golden Image Setup Script
# Prepares Wayland→X11 bridge and launches Docker environment
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   UAV MASTER HUB - GOLDEN IMAGE SETUP${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Navigate to Hub root
cd "$(dirname "$0")"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: X11 AUTHENTICATION SETUP
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}🔐 Step 1: Setting up X11 authentication...${NC}"

# Create X11 auth file
touch /tmp/.docker.xauth

# Generate X11 cookie for Docker
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f /tmp/.docker.xauth nmerge - 2>/dev/null || true

# Set permissions
chmod 644 /tmp/.docker.xauth

echo -e "${GREEN}✅ X11 auth file created: /tmp/.docker.xauth${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: XHOST PERMISSIONS
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}🔓 Step 2: Granting Docker X11 access...${NC}"

# Allow Docker to connect to X11 server
xhost +local:docker > /dev/null 2>&1

echo -e "${GREEN}✅ Docker granted X11 access${NC}"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: VERIFY DISPLAY
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}🖥️  Step 3: Verifying display configuration...${NC}"

if [ -z "$DISPLAY" ]; then
    echo -e "${RED}❌ ERROR: DISPLAY variable not set!${NC}"
    echo -e "${YELLOW}This usually means you're not in a graphical session.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ DISPLAY=$DISPLAY${NC}"

# Check session type
SESSION_TYPE=$(echo $XDG_SESSION_TYPE)
echo -e "${GREEN}✅ Session Type: $SESSION_TYPE${NC}"

if [ "$SESSION_TYPE" = "wayland" ]; then
    echo -e "${YELLOW}⚠️  Wayland detected - Using Xwayland bridge${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: CHECK DOCKER
# ═══════════════════════════════════════════════════════════════════════════

echo -e "${YELLOW}🐳 Step 4: Checking Docker installation...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ ERROR: Docker not installed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker found: $(docker --version)${NC}"

# Check if user is in docker group
if ! groups | grep -q docker; then
    echo -e "${YELLOW}⚠️  WARNING: User not in docker group${NC}"
    echo -e "${YELLOW}You may need to use sudo or add yourself to docker group:${NC}"
    echo -e "${YELLOW}  sudo usermod -aG docker \$USER${NC}"
    echo -e "${YELLOW}  Then log out and log back in${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: BUILD OR RUN
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   READY TO LAUNCH${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Choose an option:${NC}"
echo -e "  ${GREEN}1${NC}) Build Golden Image (first time or after changes)"
echo -e "  ${GREEN}2${NC}) Run existing Golden Image"
echo -e "  ${GREEN}3${NC}) Build and Run (clean rebuild)"
echo -e "  ${GREEN}4${NC}) Exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo -e "${YELLOW}🏗️  Building Golden Image...${NC}"
        docker compose -f docker-compose.golden.yml build
        echo -e "${GREEN}✅ Build complete!${NC}"
        echo -e "${YELLOW}Run: docker compose -f docker-compose.golden.yml up${NC}"
        ;;
    2)
        echo -e "${YELLOW}🚀 Launching Golden Image...${NC}"
        docker compose -f docker-compose.golden.yml up
        ;;
    3)
        echo -e "${YELLOW}🏗️  Clean rebuild...${NC}"
        docker compose -f docker-compose.golden.yml build --no-cache
        echo -e "${YELLOW}🚀 Launching...${NC}"
        docker compose -f docker-compose.golden.yml up
        ;;
    4)
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# ═══════════════════════════════════════════════════════════════════════════
# CLEANUP ON EXIT
# ═══════════════════════════════════════════════════════════════════════════

cleanup() {
    echo ""
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    # Optionally revoke X11 access (commented out for convenience)
    # xhost -local:docker
    echo -e "${GREEN}✅ Done${NC}"
}

trap cleanup EXIT
