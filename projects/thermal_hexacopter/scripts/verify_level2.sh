#!/bin/bash
# verify_level2.sh - Helper script to run Level 2 Survey Grid Mission

echo "========================================================"
echo "🚁 Level 2: GPS Survey Grid - Verification Helper"
echo "========================================================"
echo "This script will help you launch the mission node."
echo "Ensure you have the simulation running in another terminal!"
echo "If not, run: ./test_hover.sh"
echo "And bridge: MicroXRCEAgent udp4 -p 8888"
echo "========================================================"
echo ""
echo "🚀 Launching Mission Node..."
echo ""

# Source the environment
source /opt/ros/humble/setup.bash
source /root/workspace/install/setup.bash

# Run the node
ros2 run agri_hexacopter level2_survey_grid
