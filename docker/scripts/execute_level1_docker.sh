#!/bin/bash
# execute_level1_docker.sh - Execute Level 1 Hover Test in Docker
# Uses hexacopter_lab_safe_copy image with full ROS 2 + PX4 environment

echo "🚁 PhD DIMENSION 2 - Level 1 Hover Test Execution"
echo "=================================================="
echo ""

# Configuration
DOCKER_IMAGE="hexacopter_lab_safe_copy:latest"
CONTAINER_NAME="phd_level1_hover_test"

# Enable X11 forwarding for Gazebo
echo "📺 Enabling X11 forwarding for Gazebo GUI..."
xhost +local:docker 2>/dev/null

# Clean up any existing container
docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

echo "🐳 Starting Docker container..."
docker run -d \
  --name $CONTAINER_NAME \
  --network host \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v ~/uav_master_hub/data:/data \
  $DOCKER_IMAGE \
  sleep infinity

# Wait for container to be ready
sleep 2

echo "✅ Container started. Executing Level 1 hover test..."
echo ""
echo "This will:"
echo "  1. Start PX4 SITL with Gazebo"
echo "  2. Launch MicroXRCE-DDS bridge"
echo "  3. Execute 5m hover test"
echo "  4. Record telemetry to .ulg log"
echo ""
echo "⏱️  Expected duration: 2-3 minutes"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Execute test inside container
docker exec -it $CONTAINER_NAME bash -c '
# Setup environment
export WORKSPACE_DIR="/root/workspace"
export PX4_DIR="/root/PX4-Autopilot"

# Cleanup any previous processes
pkill -9 ruby || true
pkill -9 gz || true  
pkill -9 MicroXRCEAgent || true

# Source ROS 2
source /opt/ros/humble/setup.bash 2>/dev/null || echo "⚠️  ROS 2 not at /opt/ros/humble"

# Start MicroXRCE-DDS Bridge
echo "🌉 Starting MicroXRCE-DDS Bridge..."
MicroXRCEAgent udp4 -p 8888 &
sleep 2

# Set environment variables
export GZ_SIM_RESOURCE_PATH="$WORKSPACE_DIR/models:$PX4_DIR/Tools/simulation/gz/models"
export PX4_HOME_LAT=25.344644  # Bihar coordinates
export PX4_HOME_LON=86.483958

# Launch PX4 SITL
echo "🚀 Launching PX4 SITL with Gazebo..."
cd $PX4_DIR
PX4_GZ_WORLD=default PX4_GZ_MODEL=x500 make px4_sitl gz_x500
'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Test execution complete!"
echo ""
echo "📊 Next steps:"
echo "  1. Extract telemetry log from container"
echo "  2. Run flight_dynamics_analysis.py"
echo "  3. Generate Bode plots and step response"
echo ""
echo "Run this to extract logs:"
echo "  docker cp $CONTAINER_NAME:/root/PX4-Autopilot/build/px4_sitl_default/tmp/log ~/uav_master_hub/data/telemetry_logs/"
echo ""
