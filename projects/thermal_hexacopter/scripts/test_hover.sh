#!/bin/bash
# test_hover.sh - The "Minimalist" Verification Script

# 1. Setup Paths
WORKSPACE_DIR="/root/workspace"
PX4_DIR="/root/PX4-Autopilot"

# 2. Cleanup & Sync
pkill -9 ruby || true; pkill -9 gz || true; pkill -9 MicroXRCEAgent || true
source /opt/ros/humble/setup.bash
source "$WORKSPACE_DIR/install/setup.bash"

# 3. Start the Bridge
MicroXRCEAgent udp4 -p 8888 &
sleep 2

# 4. Environment
export GZ_SIM_RESOURCE_PATH="$WORKSPACE_DIR/models:$PX4_DIR/Tools/simulation/gz/models"
export PX4_HOME_LAT=25.344644
export PX4_HOME_LON=86.483958

# 5. The "Standard" Launch
# We use the 'default' world which has no external mesh dependencies
echo "🚀 Launching Minimalist Test (Default World)..."
PX4_GZ_WORLD=default \
PX4_GZ_MODEL=x500 \
make -C "$PX4_DIR" px4_sitl gz_x500