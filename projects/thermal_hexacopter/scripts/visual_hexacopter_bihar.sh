#!/bin/bash
# visual_hexacopter_bihar.sh - High-Fidelity Bihar Mission Launch Script
# CEO Master Directive: Phase 2 - Real Experience with Bihar World

WORKSPACE_DIR="/root/workspace"
PX4_DIR="/root/PX4-Autopilot"

echo "🌾 BIHAR MISSION: High-Fidelity Agricultural Simulation"
echo "=================================================="

# 1. Aggressive Cleanup
echo "🧹 Cleaning previous processes..."
pkill -9 ruby || true
pkill -9 gz || true
pkill -9 MicroXRCEAgent || true
pkill -9 px4 || true
sleep 1

# 2. Source ROS 2 Environment
echo "🔧 Sourcing ROS 2 Humble..."
source /opt/ros/humble/setup.bash
source "$WORKSPACE_DIR/install/setup.bash"

# 3. Start the ROS 2 Bridge
echo "🌉 Starting MicroXRCEAgent (UDP Port 8888)..."
MicroXRCEAgent udp4 -p 8888 &
AGENT_PID=$!
sleep 2

# 4. Environment & Paths
echo "📂 Configuring Gazebo resource paths..."
export GZ_SIM_RESOURCE_PATH="$WORKSPACE_DIR/models:$WORKSPACE_DIR/src/agri_hexacopter/worlds:$PX4_DIR/Tools/simulation/gz/models"

# 5. Bihar GPS Coordinates (Samastipur District)
echo "📍 Setting Bihar GPS coordinates..."
export PX4_HOME_LAT=25.344644
export PX4_HOME_LON=86.483958
export PX4_HOME_ALT=50.0

# 6. Model Configuration
echo "🚁 Configuring hexacopter model..."
export PX4_SIM_MODEL=agri_hexacopter_drone
export PX4_GZ_MODEL=agri_hexacopter_drone

# 7. Bihar World Selection
echo "🌾 Loading Bihar Maize Farm World..."
export PX4_GZ_WORLD=bihar_maize

# 8. Launch Simulation with VTOL Mixer
echo "🚀 Launching PX4 SITL with Bihar World..."
echo "   - World: bihar_maize"
echo "   - Model: agri_hexacopter_drone"
echo "   - Mixer: gz_standard_vtol (hexacopter physics)"
echo "   - GPS: 25.344644°N, 86.483958°E (Bihar, India)"
echo ""
echo "✅ Ready for mission execution!"
echo "   Terminal 2: ros2 run agri_hexacopter thermal_monitor"
echo "   Terminal 3: /root/workspace/install/agri_bot_missions/bin/level3_survey"
echo ""

# Launch with Bihar world
cd "$PX4_DIR"
make px4_sitl gz_standard_vtol

# Cleanup on exit
trap "kill $AGENT_PID 2>/dev/null" EXIT
