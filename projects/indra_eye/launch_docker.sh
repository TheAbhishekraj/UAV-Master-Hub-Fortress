#!/bin/bash
###############################################################################
# Indra-Eye: Docker Launch with hexacopter_lab_golden
#
# Launches Indra-Eye system inside the hexacopter_lab_golden Docker container
# with X11 forwarding for GUI applications (Gazebo, RViz, QGC)
#
# Usage:
#   bash launch_docker.sh
#
# Author: Indra-Eye Development Team
# License: MIT
###############################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/abhishek/thermal_hexacopter_project/indra_eye_project"
DOCKER_IMAGE="hexacopter_lab_golden:latest"
CONTAINER_NAME="indra_eye_mission"

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header "Indra-Eye Docker Launcher"

# Check if Docker image exists
if ! docker images | grep -q "hexacopter_lab_golden"; then
    print_error "Docker image 'hexacopter_lab_golden' not found"
    print_info "Available images:"
    docker images
    exit 1
fi

print_success "Docker image found: $DOCKER_IMAGE"

# Stop and remove existing container
print_info "Cleaning up existing containers..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Setup X11 forwarding
print_info "Setting up X11 forwarding..."
xhost +local:docker

# Create temporary X11 auth file
XAUTH=/tmp/.docker.xauth
touch $XAUTH 2>/dev/null || XAUTH=$HOME/.Xauthority
xauth nlist $DISPLAY | sed -e 's/^..../ffff/' | xauth -f $XAUTH nmerge - 2>/dev/null || true

print_header "Launching Docker Container"

# Run Docker container with GUI support
docker run -it --rm \
    --name $CONTAINER_NAME \
    --privileged \
    --network host \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --env XAUTHORITY=/tmp/.docker.xauth \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume $PROJECT_DIR:/home/user/indra_eye_project:rw \
    --volume $XAUTH:/tmp/.docker.xauth:ro \
    --device /dev/dri \
    --workdir /home/user/indra_eye_project \
    $DOCKER_IMAGE \
    bash -c "
        echo -e '${BLUE}========================================${NC}'
        echo -e '${BLUE}Indra-Eye Docker Environment${NC}'
        echo -e '${BLUE}========================================${NC}'
        echo ''
        echo -e '${GREEN}✓${NC} Docker container running'
        echo -e '${GREEN}✓${NC} X11 forwarding enabled'
        echo -e '${GREEN}✓${NC} Project mounted at /home/user/indra_eye_project'
        echo ''
        
        # Source ROS 2
        source /opt/ros/humble/setup.bash
        
        # Navigate to project
        cd /home/user/indra_eye_project
        
        # Build workspace if not built
        if [ ! -d 'install' ]; then
            echo -e '${YELLOW}[INFO]${NC} Building workspace...'
            colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
            echo -e '${GREEN}[SUCCESS]${NC} Workspace built'
        else
            echo -e '${GREEN}✓${NC} Workspace already built'
        fi
        
        # Source workspace
        source install/setup.bash
        
        echo ''
        echo -e '${BLUE}========================================${NC}'
        echo -e '${BLUE}Launch Options${NC}'
        echo -e '${BLUE}========================================${NC}'
        echo ''
        echo -e '${CYAN}1. Multi-Terminal Launch:${NC}'
        echo -e '   bash launch_multi_terminal.sh'
        echo ''
        echo -e '${CYAN}2. TMux Launch:${NC}'
        echo -e '   bash launch_tmux.sh'
        echo ''
        echo -e '${CYAN}3. Python Master Launcher:${NC}'
        echo -e '   python3 fly.py --mode sitl --qgc'
        echo ''
        echo -e '${CYAN}4. Manual Launch:${NC}'
        echo -e '   ros2 launch indra_eye_sim sitl_launch.py'
        echo ''
        echo -e '${YELLOW}Starting multi-terminal launcher in 5 seconds...${NC}'
        echo -e '${YELLOW}Press Ctrl+C to cancel and choose manually${NC}'
        sleep 5
        
        # Launch multi-terminal
        bash launch_multi_terminal.sh
    "

# Cleanup
xhost -local:docker

print_success "Docker container stopped"
exit 0
