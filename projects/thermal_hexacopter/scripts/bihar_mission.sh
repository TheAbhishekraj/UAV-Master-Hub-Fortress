#!/bin/bash

# deploy_and_fly.sh
# Automates Structural Audit and Launch for PX4/Gazebo Digital Twin

# 1. Detect Workspace Root (Works in Docker /root/workspace or Local)
WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📍 Workspace: $WORKSPACE_DIR"

# 2. Define Paths & Constants
MODEL_NAME="agri_hexacopter_drone"
WORLD_FILE="bihar_maize.sdf"

# Detect PX4 Directory (Local vs Docker)
if [ -d "/root/PX4-Autopilot" ]; then
    PX4_DIR="/root/PX4-Autopilot"
else
    PX4_DIR="$HOME/PX4-Autopilot"
fi

# --- AUDIT CHECKS ---

echo "🔍 Running Pre-Flight Checks..."

# Q1: Identity Check (model.config)
MODEL_CONFIG="$WORKSPACE_DIR/models/$MODEL_NAME/model.config"
if [ ! -f "$MODEL_CONFIG" ]; then
    echo "❌ Error: model.config missing at $MODEL_CONFIG"
    exit 1
fi

# Check if <name> tag matches folder name
if ! grep -E -q "<name>[[:space:]]*$MODEL_NAME[[:space:]]*</name>" "$MODEL_CONFIG"; then
    echo "❌ Identity Mismatch: <name> in model.config must be '$MODEL_NAME'"
    exit 1
else
    echo "✅ Identity Check: Passed"
fi

# Q2: Ghost Extension Check (.sdf.sdf)
WORLDS_DIR="$WORKSPACE_DIR/src/agri_hexacopter/worlds"
if [ ! -d "$WORLDS_DIR" ]; then
    echo "❌ Error: Worlds directory missing at $WORLDS_DIR"
    exit 1
fi

if ls "$WORLDS_DIR"/*.sdf.sdf 1> /dev/null 2>&1; then
    echo "❌ Ghost File Detected: Found .sdf.sdf files in $WORLDS_DIR"
    exit 1
else
    echo "✅ Extension Check: Passed"
fi

# --- LAUNCH SEQUENCE ---

echo "🚀 Standardizing Paths and Initializing..."

# 1. Source ROS 2 and Workspace
source /opt/ros/humble/setup.bash
source "$WORKSPACE_DIR/install/setup.bash"

# 2. DEPLOY: Push your world into the PX4 internal folder
# This prevents the "Double Path" error
cp "$WORKSPACE_DIR/src/agri_hexacopter/worlds/bihar_maize.sdf" "$PX4_DIR/Tools/simulation/gz/worlds/bihar_maize.sdf"

# 3. Cleanup previous sessions
pkill -9 ruby || true; pkill -9 gz || true; pkill -9 MicroXRCEAgent || true

# 4. Start Bridge
MicroXRCEAgent udp4 -p 8888 &
sleep 2

# 5. Configure Environment
export GZ_SIM_RESOURCE_PATH="$WORKSPACE_DIR/models:$PX4_DIR/Tools/simulation/gz/models"
export PX4_HOME_LAT=25.344644
export PX4_HOME_LON=86.483958

# 6. Launch using SHORT NAMES ONLY
# Notice: No path, no .sdf extension. PX4 will find it in its internal folder.
PX4_GZ_WORLD=bihar_maize \
PX4_GZ_MODEL=agri_hexacopter_drone \
make -C "$PX4_DIR" px4_sitl gz_x500