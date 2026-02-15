#!/bin/bash
###############################################################################
# Indra-Eye: Master Mission Launch Script
# 
# Single-command launch for complete mission stack (SITL or HITL mode)
#
# Usage:
#   bash run_mission.sh --sitl          # Simulation mode (Gazebo + PX4 SITL)
#   bash run_mission.sh --hitl          # Hardware-in-the-Loop (real sensors)
#   bash run_mission.sh --sitl --record # SITL with mission recording
#   bash run_mission.sh --hitl --qgc    # HITL with QGroundControl
#
# Author: Indra-Eye Development Team
# License: MIT
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

###############################################################################
# Helper Functions
###############################################################################

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

cleanup() {
    print_info "Shutting down mission stack..."
    # Kill all background processes
    jobs -p | xargs -r kill 2>/dev/null || true
    print_success "Mission stack stopped"
}

trap cleanup EXIT INT TERM

###############################################################################
# Parse Arguments
###############################################################################

MODE=""
USE_QGC=false
USE_RECORD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --sitl)
            MODE="sitl"
            shift
            ;;
        --hitl)
            MODE="hitl"
            shift
            ;;
        --qgc)
            USE_QGC=true
            shift
            ;;
        --record)
            USE_RECORD=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 {--sitl|--hitl} [--qgc] [--record]"
            exit 1
            ;;
    esac
done

if [ -z "$MODE" ]; then
    print_error "Mode not specified. Use --sitl or --hitl"
    echo "Usage: $0 {--sitl|--hitl} [--qgc] [--record]"
    exit 1
fi

###############################################################################
# Environment Setup
###############################################################################

print_header "Indra-Eye Mission Launch - ${MODE^^} Mode"

# Source ROS 2
if [ -f "/opt/ros/humble/setup.bash" ]; then
    source /opt/ros/humble/setup.bash
    print_success "ROS 2 Humble sourced"
else
    print_error "ROS 2 Humble not found"
    exit 1
fi

# Source workspace
if [ -f "$PROJECT_DIR/install/setup.bash" ]; then
    source "$PROJECT_DIR/install/setup.bash"
    print_success "Workspace sourced"
else
    print_error "Workspace not built. Run: bash setup_and_run.sh --build"
    exit 1
fi

# Create logs directory
mkdir -p "$PROJECT_DIR/logs/rosbags"
mkdir -p "$PROJECT_DIR/logs/screenshots"

###############################################################################
# SITL Mode
###############################################################################

if [ "$MODE" == "sitl" ]; then
    print_header "Launching SITL Mission Stack"
    
    print_info "Components:"
    print_info "  ✓ Gazebo (Himalayan terrain)"
    print_info "  ✓ PX4 SITL"
    print_info "  ✓ Micro-XRCE-DDS Agent"
    print_info "  ✓ ES-EKF Node"
    print_info "  ✓ Supervisor Node"
    print_info "  ✓ MAVROS Bridge"
    print_info "  ✓ Path Aggregator"
    print_info "  ✓ RViz2"
    if [ "$USE_QGC" = true ]; then
        print_info "  ✓ QGroundControl"
    fi
    
    # Launch using ROS 2 launch file
    if [ "$USE_QGC" = true ]; then
        ros2 launch indra_eye_sim sitl_launch.py use_qgc:=true &
    else
        ros2 launch indra_eye_sim sitl_launch.py &
    fi
    
    LAUNCH_PID=$!
    
    # Wait for initialization
    sleep 5
    print_success "SITL stack launched (PID: $LAUNCH_PID)"
    
    # Optional: Start recording
    if [ "$USE_RECORD" = true ]; then
        print_info "Starting mission recording..."
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        ros2 bag record -o "$PROJECT_DIR/logs/rosbags/sitl_mission_$TIMESTAMP" \
            /px4/gnss \
            /camera/stereo/odom \
            /lidar/slam/pose \
            /indra_eye/fused_odom \
            /indra_eye/fused_pose \
            /indra_eye/navigation_mode \
            /indra_eye/spoofing_detected \
            /visualization/gps_path \
            /visualization/vio_path \
            /visualization/fused_path &
        
        RECORD_PID=$!
        print_success "Recording started (PID: $RECORD_PID)"
    fi

###############################################################################
# HITL Mode
###############################################################################

elif [ "$MODE" == "hitl" ]; then
    print_header "Launching HITL Mission Stack"
    
    # Check hardware configuration
    HARDWARE_CONFIG="$PROJECT_DIR/config/hardware_map.yaml"
    if [ ! -f "$HARDWARE_CONFIG" ]; then
        print_error "Hardware config not found: $HARDWARE_CONFIG"
        exit 1
    fi
    
    print_info "Hardware configuration: $HARDWARE_CONFIG"
    
    # Check if running in Docker
    if [ -f /.dockerenv ]; then
        print_success "Running inside Docker container"
    else
        print_error "HITL mode requires Docker environment"
        print_info "Use: docker-compose -f docker-compose.hitl.yaml up"
        exit 1
    fi
    
    # Setup network for Livox LiDAR
    print_info "Configuring network for Livox LiDAR..."
    sudo ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up 2>/dev/null || true
    sudo route add -net 192.168.1.0 netmask 255.255.255.0 dev eth0 2>/dev/null || true
    print_success "Network configured"
    
    print_info "Components:"
    print_info "  ✓ Livox Mid-360 LiDAR Driver"
    print_info "  ✓ Intel RealSense D435i Driver"
    print_info "  ✓ u-blox F9P GNSS Driver"
    print_info "  ✓ ES-EKF Node"
    print_info "  ✓ Supervisor Node"
    print_info "  ✓ MAVROS Bridge"
    print_info "  ✓ Path Aggregator"
    print_info "  ✓ RViz2"
    if [ "$USE_QGC" = true ]; then
        print_info "  ✓ QGroundControl"
    fi
    
    # Launch using HITL launch file
    if [ "$USE_QGC" = true ]; then
        ros2 launch indra_eye_sim hitl_launch.py use_qgc:=true &
    else
        ros2 launch indra_eye_sim hitl_launch.py &
    fi
    
    LAUNCH_PID=$!
    
    # Wait for initialization
    sleep 10
    print_success "HITL stack launched (PID: $LAUNCH_PID)"
    
    # Check sensor connectivity
    print_info "Checking sensor connectivity..."
    sleep 5
    
    # Check topics
    if ros2 topic list | grep -q "/livox/lidar"; then
        print_success "Livox LiDAR: Connected"
    else
        print_error "Livox LiDAR: Not detected"
    fi
    
    if ros2 topic list | grep -q "/camera/color/image_raw"; then
        print_success "RealSense Camera: Connected"
    else
        print_error "RealSense Camera: Not detected"
    fi
    
    if ros2 topic list | grep -q "/ublox/fix"; then
        print_success "u-blox GNSS: Connected"
    else
        print_error "u-blox GNSS: Not detected"
    fi
fi

###############################################################################
# Mission Monitoring
###############################################################################

print_header "Mission Active"
print_info "Press Ctrl+C to stop mission"
print_info ""
print_info "Useful commands:"
print_info "  - View topics:     ros2 topic list"
print_info "  - View diagnostics: ros2 topic echo /indra_eye/diagnostics"
print_info "  - View nav mode:   ros2 topic echo /indra_eye/navigation_mode"
print_info "  - Trigger GPS denial: ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool \"data: true\""
print_info ""

# Monitor mission (wait for user interrupt)
wait $LAUNCH_PID

###############################################################################
# Cleanup
###############################################################################

print_info "Mission completed"
exit 0
