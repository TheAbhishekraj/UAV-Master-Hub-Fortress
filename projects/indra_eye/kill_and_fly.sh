#!/bin/bash
###############################################################################
# Indra-Eye: Kill All Processes and Launch Clean
#
# This script forcefully terminates all robotics processes and launches
# a fresh SITL simulation for debugging.
#
# Usage:
#   bash kill_and_fly.sh
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

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Indra-Eye: Kill & Fly${NC}"
echo -e "${BLUE}========================================${NC}"

# Force kill all robotics processes
echo -e "${YELLOW}[INFO]${NC} Terminating all robotics processes..."
killall -9 gazebo gzserver gzclient px4 MicroXRCEAgent mavros rviz2 qgroundcontrol 2>/dev/null || true
sleep 2

# Clean up any lingering processes
pkill -9 -f "ros2 launch" 2>/dev/null || true
pkill -9 -f "indra_eye" 2>/dev/null || true
sleep 1

echo -e "${GREEN}[SUCCESS]${NC} All processes terminated"

# Clean build
echo -e "${YELLOW}[INFO]${NC} Cleaning and rebuilding workspace..."
cd /home/abhishek/thermal_hexacopter_project/indra_eye_project

# Remove old build artifacts
rm -rf build/ install/ log/ 2>/dev/null || true

# Source ROS 2
source /opt/ros/humble/setup.bash

# Build workspace
echo -e "${YELLOW}[INFO]${NC} Running colcon build..."
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[SUCCESS]${NC} Build completed"
else
    echo -e "${RED}[ERROR]${NC} Build failed"
    exit 1
fi

# Source workspace
source install/setup.bash
echo -e "${GREEN}[SUCCESS]${NC} Workspace sourced"

# Launch SITL with QGC
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Launching SITL Mission${NC}"
echo -e "${BLUE}========================================${NC}"

bash run_mission.sh --sitl --qgc

exit 0
