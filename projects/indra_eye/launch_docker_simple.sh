#!/bin/bash
###############################################################################
# Indra-Eye: Simple Docker Interactive Launch
#
# Launches an interactive shell in hexacopter_lab_golden container
# where you can manually build and run Indra-Eye
#
# Usage:
#   bash launch_docker_simple.sh
#
# Author: Indra-Eye Development Team
###############################################################################

set -e

PROJECT_DIR="/home/abhishek/thermal_hexacopter_project/indra_eye_project"
DOCKER_IMAGE="hexacopter_lab_golden:latest"
CONTAINER_NAME="indra_eye_dev"

echo "========================================"
echo "Indra-Eye Docker Interactive Shell"
echo "========================================"
echo ""

# Setup X11
xhost +local:docker 2>/dev/null || true

# Create X auth
XAUTH=/tmp/.docker.xauth
touch $XAUTH 2>/dev/null || XAUTH=$HOME/.Xauthority
xauth nlist $DISPLAY 2>/dev/null | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge - 2>/dev/null || true

# Stop existing container
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "Starting Docker container..."
echo ""

# Run interactive container
docker run -it --rm \
    --name $CONTAINER_NAME \
    --privileged \
    --network host \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume $PROJECT_DIR:/workspace/indra_eye_project:rw \
    --volume $XAUTH:/tmp/.docker.xauth:ro \
    --env XAUTHORITY=/tmp/.docker.xauth \
    --device /dev/dri \
    --workdir /workspace/indra_eye_project \
    $DOCKER_IMAGE \
    bash -c '
echo "========================================="
echo "Indra-Eye Development Environment"
echo "========================================="
echo ""
echo "✓ Container: hexacopter_lab_golden"
echo "✓ Project: /workspace/indra_eye_project"
echo "✓ X11: Enabled for GUI apps"
echo ""
echo "========================================="
echo "Quick Start Commands"
echo "========================================="
echo ""
echo "1. Check ROS 2 installation:"
echo "   which ros2"
echo "   ros2 --version"
echo ""
echo "2. If ROS 2 is available, build workspace:"
echo "   source /opt/ros/humble/setup.bash  # or your ROS distro"
echo "   colcon build --symlink-install"
echo ""
echo "3. Launch Indra-Eye:"
echo "   source install/setup.bash"
echo "   bash launch_multi_terminal.sh"
echo ""
echo "4. Or use Python launcher:"
echo "   python3 fly.py --mode sitl --qgc"
echo ""
echo "========================================="
echo ""

# Drop into interactive bash
exec bash
'

# Cleanup
xhost -local:docker 2>/dev/null || true

echo ""
echo "Container stopped"
