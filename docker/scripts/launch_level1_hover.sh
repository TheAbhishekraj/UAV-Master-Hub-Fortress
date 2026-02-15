#!/usr/bin/env bash
################################################################################
# Level 1 Hover Test - Complete Launch Script
# UAV Master Hub - Phase 2: Digital Handshake
#
# This script launches PX4 SITL with bihar_maize.sdf world and executes
# the Level 1 hover test with stability monitoring.
#
# Author: Abhishek Raj, IIT Patna
# Date: February 15, 2026
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Hub paths (all relative to uav_master_hub)
HUB_ROOT="/home/abhishek/uav_master_hub"
WORLD_FILE="${HUB_ROOT}/assets/worlds/bihar_maize.sdf"
MODEL_DIR="${HUB_ROOT}/assets/models/agri_hexacopter_drone"
THERMAL_PROJECT="${HUB_ROOT}/projects/thermal_hexacopter"
PX4_ROOT="${HOME}/PX4-Autopilot"

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   UAV MASTER HUB - LEVEL 1 HOVER TEST LAUNCHER${NC}"
echo -e "${BLUE}   Phase 2: Digital Handshake (Stability & EKF2 Audit)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Pre-flight checks
echo -e "${YELLOW}🔍 Pre-flight Checks...${NC}"

# Check ROS 2 Humble
if [ ! -f /opt/ros/humble/setup.bash ]; then
    echo -e "${RED}❌ ERROR: ROS 2 Humble not installed!${NC}"
    echo -e "${YELLOW}Please install ROS 2 Humble first:${NC}"
    echo -e "  See: ${HUB_ROOT}/.gemini/antigravity/brain/.../ros2_installation_guide.md"
    exit 1
fi
echo -e "${GREEN}✅ ROS 2 Humble found${NC}"

# Check PX4-Autopilot
if [ ! -d "${PX4_ROOT}" ]; then
    echo -e "${RED}❌ ERROR: PX4-Autopilot not found at ${PX4_ROOT}${NC}"
    echo -e "${YELLOW}Please clone PX4-Autopilot:${NC}"
    echo -e "  git clone https://github.com/PX4/PX4-Autopilot.git ~/PX4-Autopilot"
    exit 1
fi
echo -e "${GREEN}✅ PX4-Autopilot found${NC}"

# Check workspace built
if [ ! -d "${THERMAL_PROJECT}/install" ]; then
    echo -e "${YELLOW}⚠️  Workspace not built. Building now...${NC}"
    cd "${THERMAL_PROJECT}"
    source /opt/ros/humble/setup.bash
    colcon build --symlink-install --packages-select agri_hexacopter agri_bot_missions
    echo -e "${GREEN}✅ Workspace built${NC}"
else
    echo -e "${GREEN}✅ Workspace already built${NC}"
fi

# Check world file
if [ ! -f "${WORLD_FILE}" ]; then
    echo -e "${RED}❌ ERROR: bihar_maize.sdf not found at ${WORLD_FILE}${NC}"
    exit 1
fi
echo -e "${GREEN}✅ bihar_maize.sdf world found${NC}"

# Check model directory
if [ ! -d "${MODEL_DIR}" ]; then
    echo -e "${RED}❌ ERROR: agri_hexacopter_drone model not found at ${MODEL_DIR}${NC}"
    exit 1
fi
echo -e "${GREEN}✅ agri_hexacopter_drone model found${NC}"

echo ""
echo -e "${GREEN}✅ All pre-flight checks passed!${NC}"
echo ""

# Copy world file to PX4 (if not already there)
PX4_WORLD_DIR="${PX4_ROOT}/Tools/simulation/gz/worlds"
if [ ! -f "${PX4_WORLD_DIR}/bihar_maize.sdf" ]; then
    echo -e "${YELLOW}📋 Copying bihar_maize.sdf to PX4 worlds directory...${NC}"
    cp "${WORLD_FILE}" "${PX4_WORLD_DIR}/"
    echo -e "${GREEN}✅ World file copied${NC}"
fi

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   LAUNCH SEQUENCE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}This script will guide you through launching 3 terminals:${NC}"
echo ""
echo -e "${GREEN}Terminal 1:${NC} PX4 SITL with Gazebo (bihar_maize.sdf world)"
echo -e "${GREEN}Terminal 2:${NC} ROS 2 Level 1 hover mission"
echo -e "${GREEN}Terminal 3:${NC} Hover stability monitor (position error + EKF2)"
echo ""
echo -e "${YELLOW}Press ENTER to see Terminal 1 command...${NC}"
read

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   TERMINAL 1: PX4 SITL + Gazebo${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Open a NEW terminal and run:${NC}"
echo ""
echo -e "${GREEN}cd ~/PX4-Autopilot${NC}"
echo -e "${GREEN}PX4_GZ_WORLD=bihar_maize make px4_sitl gz_x500${NC}"
echo ""
echo -e "${YELLOW}Wait for:${NC}"
echo -e "  • Gazebo GUI to open"
echo -e "  • Hexacopter to spawn in Bihar maize field"
echo -e "  • 'pxh>' prompt in terminal"
echo -e "  • Message: 'Ready for takeoff!'"
echo ""
echo -e "${YELLOW}Press ENTER when Terminal 1 is ready...${NC}"
read

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   TERMINAL 2: ROS 2 Hover Mission${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Open a NEW terminal and run:${NC}"
echo ""
echo -e "${GREEN}cd ${THERMAL_PROJECT}${NC}"
echo -e "${GREEN}source /opt/ros/humble/setup.bash${NC}"
echo -e "${GREEN}source install/setup.bash${NC}"
echo -e "${GREEN}ros2 run agri_hexacopter level1_basic_takeoff${NC}"
echo ""
echo -e "${YELLOW}Expected behavior:${NC}"
echo -e "  • Waits 1 second (20 setpoints at 20Hz)"
echo -e "  • Arms motors"
echo -e "  • Takes off to 5 meters"
echo -e "  • Hovers indefinitely"
echo ""
echo -e "${YELLOW}Press ENTER when Terminal 2 is running...${NC}"
read

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   TERMINAL 3: Stability Monitor (PhD Proof)${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Open a NEW terminal and run:${NC}"
echo ""
echo -e "${GREEN}cd ${HUB_ROOT}${NC}"
echo -e "${GREEN}source /opt/ros/humble/setup.bash${NC}"
echo -e "${GREEN}python3 tools/hover_stability_monitor.py${NC}"
echo ""
echo -e "${YELLOW}This will display:${NC}"
echo -e "  • Real-time position error (target vs actual)"
echo -e "  • Horizontal/vertical error statistics"
echo -e "  • EKF2 innovation bounds"
echo -e "  • PhD precision assessment"
echo ""
echo -e "${YELLOW}Let it run for 60+ seconds, then Ctrl+C for final summary${NC}"
echo ""
echo -e "${YELLOW}Press ENTER to continue...${NC}"
read

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   TEST IN PROGRESS${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✅ All terminals should now be running!${NC}"
echo ""
echo -e "${YELLOW}Monitor the following:${NC}"
echo -e "  • Terminal 1: Drone hovering in Gazebo"
echo -e "  • Terminal 2: Setpoint publishing messages"
echo -e "  • Terminal 3: Stability reports every 1 second"
echo ""
echo -e "${YELLOW}Success Criteria:${NC}"
echo -e "  ✅ Horizontal position error RMS < 0.3m"
echo -e "  ✅ EKF2 innovation < 0.5m"
echo -e "  ✅ Velocity < 0.1 m/s (stable hover)"
echo -e "  ✅ No oscillations or drift"
echo ""
echo -e "${YELLOW}After 60+ seconds:${NC}"
echo -e "  1. Ctrl+C in Terminal 3 (view final summary)"
echo -e "  2. Ctrl+C in Terminal 2 (stop mission, drone lands)"
echo -e "  3. Ctrl+C in Terminal 1 (stop PX4 SITL)"
echo ""
echo -e "${YELLOW}Post-Flight:${NC}"
echo -e "  • Find .ulg log: ~/PX4-Autopilot/build/px4_sitl_default/logs/"
echo -e "  • Copy to Hub: ${HUB_ROOT}/field_evidence/logs/"
echo -e "  • Analyze: python3 tools/flight_dynamics_analysis.py <log_file>"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚁 LEVEL 1 HOVER TEST INITIATED - Good luck!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
