#!/bin/bash
# test_hover_hub.sh - UAV Master Hub Compatible Version
# Fixed paths for uav_hub_master:v1 Docker image

# 1. Setup Paths (CORRECTED FOR DOCKERFILE)
WORKSPACE_DIR="/root/hexacopter_phd"    # ✅ FIXED: Matches Dockerfile ENV
PX4_DIR="/root/PX4-Autopilot"

# 2. Cleanup & Sync
echo "🧹 Cleaning up previous processes..."
pkill -9 ruby || true
pkill -9 gz || true
pkill -9 MicroXRCEAgent || true

echo "🔧 Sourcing ROS 2 environment..."
source /opt/ros/humble/setup.bash
source "$WORKSPACE_DIR/install/setup.bash"

# 3. Start the Bridge
echo "🌉 Starting MicroXRCE-DDS Bridge..."
MicroXRCEAgent udp4 -p 8888 &
sleep 2

# 4. Environment
echo "🌍 Setting up Gazebo environment..."
export GZ_SIM_RESOURCE_PATH="$WORKSPACE_DIR/assets/models:$PX4_DIR/Tools/simulation/gz/models"
export PX4_HOME_LAT=25.344644  # Bihar coordinates
export PX4_HOME_LON=86.483958

# 5. The "Standard" Launch
echo "🚀 Launching Level 1 Hover Test (Default World)..."
echo "📍 Home Position: Bihar, India (25.344644, 86.483958)"
echo ""

PX4_GZ_WORLD=default \
PX4_GZ_MODEL=x500 \
make -C "$PX4_DIR" px4_sitl gz_x500
