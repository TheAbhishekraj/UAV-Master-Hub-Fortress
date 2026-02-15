#!/bin/bash
# DIMENSION 2 EXECUTION - Level 1 Hover Test (Using Legacy Environment)
# This script executes the Level 1 hover test using the proven legacy workspace
# Results will be migrated back to Hub after completion

set -e

echo "════════════════════════════════════════════════════════════════"
echo "🚁 DIMENSION 2: ROBOTICS & FLIGHT CONTROL VALIDATION"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Strategy: Using legacy environment (proven working)"
echo "Location: /home/abhishek/thermal_hexacopter_project/ros2_ws"
echo ""

# Navigate to legacy workspace
cd /home/abhishek/thermal_hexacopter_project/ros2_ws

# Check ROS 2 Humble
if [ ! -f /opt/ros/humble/setup.bash ]; then
    echo "❌ ERROR: ROS 2 Humble not found!"
    echo "Please install ROS 2 Humble or use Option B from docker_resolution_strategy.md"
    exit 1
fi

echo "✅ ROS 2 Humble found"
echo ""

# Source ROS 2
source /opt/ros/humble/setup.bash
echo "✅ Sourced ROS 2 Humble"

# Check if workspace is built
if [ ! -d "install" ]; then
    echo "⚙️  Building workspace (first time)..."
    colcon build --symlink-install --packages-select agri_hexacopter agri_bot_missions
    echo "✅ Workspace built"
else
    echo "✅ Workspace already built"
fi

# Source workspace
source install/setup.bash
echo "✅ Sourced workspace"
echo ""

# Verify packages
echo "📦 Verifying ROS 2 packages..."
if ros2 pkg list | grep -q agri_hexacopter; then
    echo "  ✅ agri_hexacopter found"
else
    echo "  ❌ agri_hexacopter NOT found"
    exit 1
fi

if ros2 pkg list | grep -q agri_bot_missions; then
    echo "  ✅ agri_bot_missions found"
else
    echo "  ❌ agri_bot_missions NOT found"
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ PRE-FLIGHT CHECKS COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🚀 READY TO LAUNCH LEVEL 1 HOVER TEST"
echo ""
echo "You need 3 terminals:"
echo ""
echo "Terminal 1 (PX4 SITL):"
echo "  cd ~/PX4-Autopilot"
echo "  make px4_sitl gz_x500"
echo ""
echo "Terminal 2 (ROS 2 Mission) - THIS TERMINAL:"
echo "  cd /home/abhishek/thermal_hexacopter_project/ros2_ws"
echo "  source /opt/ros/humble/setup.bash"
echo "  source install/setup.bash"
echo "  ros2 run agri_bot_missions level1_basic_takeoff"
echo ""
echo "Terminal 3 (Monitor):"
echo "  source /opt/ros/humble/setup.bash"
echo "  ros2 topic echo /fmu/out/vehicle_local_position"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Press ENTER when Terminal 1 (PX4 SITL) is ready..."
read

echo ""
echo "🚁 Launching Level 1 hover test..."
echo ""

# Launch the mission
ros2 run agri_bot_missions level1_basic_takeoff

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "✅ LEVEL 1 HOVER TEST COMPLETE"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Find .ulg log file in ~/PX4-Autopilot/build/px4_sitl_default/logs/"
echo "2. Copy to Hub: cp <log_file> /home/abhishek/uav_master_hub/field_evidence/logs/"
echo "3. Analyze: python3 /home/abhishek/uav_master_hub/tools/flight_dynamics_analysis.py <log_file>"
echo "4. Document results in dimension2_validation_results.md"
echo ""
