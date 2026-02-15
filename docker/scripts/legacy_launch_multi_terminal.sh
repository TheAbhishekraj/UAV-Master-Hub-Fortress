#!/bin/bash
###############################################################################
# Indra-Eye: Multi-Terminal Master Launcher
#
# Opens multiple terminal windows for complete mission stack visualization:
# - Terminal 1: Gazebo + PX4 SITL
# - Terminal 2: ES-EKF + Supervisor
# - Terminal 3: MAVROS + DDS Agent
# - Terminal 4: RViz
# - Terminal 5: Mission Monitor
# - QGroundControl (separate window)
#
# Usage:
#   bash launch_multi_terminal.sh
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
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="/home/abhishek/thermal_hexacopter_project"

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

# Check if gnome-terminal is available
if ! command -v gnome-terminal &> /dev/null; then
    print_error "gnome-terminal not found. Installing..."
    sudo apt-get update && sudo apt-get install -y gnome-terminal
fi

print_header "Indra-Eye Multi-Terminal Launcher"

# Kill existing processes
print_info "Cleaning up existing processes..."
killall -9 gazebo gzserver gzclient px4 MicroXRCEAgent mavros rviz2 qgroundcontrol 2>/dev/null || true
sleep 2
print_success "Cleanup complete"

# Source workspace
cd "$PROJECT_DIR"
source /opt/ros/humble/setup.bash 2>/dev/null || true
source install/setup.bash 2>/dev/null || print_info "Workspace not built yet - some terminals may fail"

print_header "Launching Terminal Windows"

# Terminal 1: Gazebo + PX4 SITL
print_info "Terminal 1: Gazebo + PX4 SITL"
gnome-terminal --title="Indra-Eye: Gazebo + PX4 SITL" \
    --geometry=100x30+0+0 \
    -- bash -c "
    echo -e '${CYAN}========================================${NC}'
    echo -e '${CYAN}Terminal 1: Gazebo + PX4 SITL${NC}'
    echo -e '${CYAN}========================================${NC}'
    cd $PROJECT_DIR
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    echo -e '${YELLOW}[INFO]${NC} Launching Gazebo...'
    sleep 3
    ros2 launch indra_eye_sim sitl_launch.py use_rviz:=false use_qgc:=false
    exec bash
" &

sleep 5

# Terminal 2: ES-EKF + Supervisor
print_info "Terminal 2: ES-EKF + Supervisor"
gnome-terminal --title="Indra-Eye: ES-EKF + Supervisor" \
    --geometry=100x30+800+0 \
    -- bash -c "
    echo -e '${CYAN}========================================${NC}'
    echo -e '${CYAN}Terminal 2: ES-EKF + Supervisor${NC}'
    echo -e '${CYAN}========================================${NC}'
    cd $PROJECT_DIR
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    echo -e '${YELLOW}[INFO]${NC} Waiting for PX4 to start...'
    sleep 10
    echo -e '${YELLOW}[INFO]${NC} Launching ES-EKF node...'
    ros2 run indra_eye_core es_ekf_node &
    sleep 2
    echo -e '${YELLOW}[INFO]${NC} Launching Supervisor node...'
    ros2 run indra_eye_supervisor supervisor_node &
    echo -e '${GREEN}[SUCCESS]${NC} Core nodes running'
    echo -e ''
    echo -e '${CYAN}Monitor diagnostics:${NC}'
    echo -e '  ros2 topic echo /indra_eye/diagnostics'
    echo -e ''
    echo -e '${CYAN}Check navigation mode:${NC}'
    echo -e '  ros2 topic echo /indra_eye/navigation_mode'
    exec bash
" &

sleep 3

# Terminal 3: MAVROS + DDS Agent
print_info "Terminal 3: MAVROS + DDS Agent"
gnome-terminal --title="Indra-Eye: MAVROS + DDS" \
    --geometry=100x30+0+500 \
    -- bash -c "
    echo -e '${CYAN}========================================${NC}'
    echo -e '${CYAN}Terminal 3: MAVROS + DDS Agent${NC}'
    echo -e '${CYAN}========================================${NC}'
    cd $PROJECT_DIR
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    echo -e '${YELLOW}[INFO]${NC} Waiting for PX4...'
    sleep 12
    echo -e '${YELLOW}[INFO]${NC} Starting Micro-XRCE-DDS Agent...'
    MicroXRCEAgent udp4 -p 8888 &
    sleep 2
    echo -e '${YELLOW}[INFO]${NC} Starting MAVROS...'
    ros2 run mavros mavros_node --ros-args -p fcu_url:=udp://:14540@127.0.0.1:14557 &
    sleep 2
    echo -e '${YELLOW}[INFO]${NC} Starting MAVROS Bridge...'
    ros2 run indra_eye_core mavros_bridge_node &
    sleep 1
    echo -e '${YELLOW}[INFO]${NC} Starting Path Aggregator...'
    ros2 run indra_eye_core path_aggregator_node &
    echo -e '${GREEN}[SUCCESS]${NC} Communication nodes running'
    echo -e ''
    echo -e '${CYAN}Check MAVROS connection:${NC}'
    echo -e '  ros2 topic echo /mavros/state'
    exec bash
" &

sleep 3

# Terminal 4: RViz
print_info "Terminal 4: RViz Visualization"
gnome-terminal --title="Indra-Eye: RViz" \
    --geometry=100x30+800+500 \
    -- bash -c "
    echo -e '${CYAN}========================================${NC}'
    echo -e '${CYAN}Terminal 4: RViz Visualization${NC}'
    echo -e '${CYAN}========================================${NC}'
    cd $PROJECT_DIR
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    echo -e '${YELLOW}[INFO]${NC} Waiting for nodes to initialize...'
    sleep 15
    echo -e '${YELLOW}[INFO]${NC} Launching RViz...'
    rviz2 -d src/indra_eye_sim/rviz/indra_eye_mission.rviz
    exec bash
" &

sleep 3

# Terminal 5: Mission Monitor
print_info "Terminal 5: Mission Monitor"
gnome-terminal --title="Indra-Eye: Mission Monitor" \
    --geometry=120x40+400+200 \
    -- bash -c "
    echo -e '${CYAN}========================================${NC}'
    echo -e '${CYAN}Terminal 5: Mission Monitor & Control${NC}'
    echo -e '${CYAN}========================================${NC}'
    cd $PROJECT_DIR
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    echo -e '${YELLOW}[INFO]${NC} Waiting for system initialization...'
    sleep 18
    echo -e '${GREEN}[SUCCESS]${NC} All systems ready!'
    echo -e ''
    echo -e '${BLUE}========================================${NC}'
    echo -e '${BLUE}Indra-Eye Mission Control${NC}'
    echo -e '${BLUE}========================================${NC}'
    echo -e ''
    echo -e '${CYAN}📊 Quick Status Check:${NC}'
    echo -e ''
    echo '  ros2 topic list | grep indra_eye'
    ros2 topic list | grep indra_eye 2>/dev/null || echo '  (Waiting for topics...)'
    echo -e ''
    echo -e '${CYAN}🧪 Test GPS Denial:${NC}'
    echo -e '  ${YELLOW}ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool \"data: true\"${NC}'
    echo -e ''
    echo -e '${CYAN}📈 Monitor Diagnostics:${NC}'
    echo -e '  ${YELLOW}ros2 topic echo /indra_eye/diagnostics${NC}'
    echo -e ''
    echo -e '${CYAN}🗺️ Check Navigation Mode:${NC}'
    echo -e '  ${YELLOW}ros2 topic echo /indra_eye/navigation_mode${NC}'
    echo -e ''
    echo -e '${CYAN}📊 View Sensor Rates:${NC}'
    echo -e '  ${YELLOW}ros2 topic hz /px4/imu${NC}'
    echo -e '  ${YELLOW}ros2 topic hz /indra_eye/fused_odom${NC}'
    echo -e ''
    echo -e '${CYAN}🎮 Arm Drone (in QGC or via command):${NC}'
    echo -e '  ${YELLOW}ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool \"{value: true}\"${NC}'
    echo -e ''
    echo -e '${RED}🚨 Emergency Stop:${NC}'
    echo -e '  ${YELLOW}killall -9 gazebo px4${NC}'
    echo -e ''
    echo -e '${BLUE}========================================${NC}'
    exec bash
" &

sleep 5

# Launch QGroundControl
print_info "Launching QGroundControl..."
if command -v qgroundcontrol &> /dev/null; then
    qgroundcontrol &
    print_success "QGroundControl launched"
else
    print_error "QGroundControl not found. Install with: sudo apt install qgroundcontrol"
    print_info "You can download from: https://docs.qgroundcontrol.com/master/en/getting_started/download_and_install.html"
fi

sleep 2

print_header "All Terminals Launched"
print_success "Indra-Eye mission stack is starting up!"
print_info ""
print_info "Terminal Layout:"
print_info "  Top-Left:     Gazebo + PX4 SITL"
print_info "  Top-Right:    ES-EKF + Supervisor"
print_info "  Bottom-Left:  MAVROS + DDS Agent"
print_info "  Bottom-Right: RViz Visualization"
print_info "  Center:       Mission Monitor & Control"
print_info "  Separate:     QGroundControl"
print_info ""
print_info "Wait 30 seconds for full initialization..."
print_info ""
print_info "Press Ctrl+C in any terminal to stop that component"
print_info "Run 'killall -9 gazebo px4 MicroXRCEAgent mavros rviz2' to stop all"

exit 0
