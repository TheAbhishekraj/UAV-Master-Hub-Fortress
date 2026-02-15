#!/bin/bash
###############################################################################
# Indra-Eye: Resilient UAV Positioning System
# Master Setup and Run Script
#
# Usage:
#   bash setup_and_run.sh --install    # First-time setup
#   bash setup_and_run.sh --launch     # Launch SITL simulation
#   bash setup_and_run.sh --test       # Run validation tests
#
# Author: Indra-Eye Development Team
# License: MIT
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${GREEN}========================================${NC}"
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

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    else
        print_success "$1 is installed"
        return 0
    fi
}

###############################################################################
# Installation Function
###############################################################################

install_dependencies() {
    print_header "Installing Dependencies"
    
    # Check if running in Docker (Hexacopter Lab Golden)
    if [ -f /.dockerenv ]; then
        print_info "Running inside Docker container"
    fi
    
    # Check ROS 2 Humble
    print_info "Checking ROS 2 Humble..."
    if [ -f "/opt/ros/humble/setup.bash" ]; then
        print_success "ROS 2 Humble found"
        source /opt/ros/humble/setup.bash
    else
        print_error "ROS 2 Humble not found. Please install ROS 2 Humble first."
        print_info "Visit: https://docs.ros.org/en/humble/Installation.html"
        exit 1
    fi
    
    # Check required commands
    print_info "Checking required tools..."
    check_command "colcon" || {
        print_info "Installing colcon..."
        sudo apt-get update
        sudo apt-get install -y python3-colcon-common-extensions
    }
    
    check_command "gazebo" || {
        print_info "Installing Gazebo..."
        sudo apt-get install -y gazebo libgazebo-dev
    }
    
    # Install Eigen3
    print_info "Checking Eigen3..."
    if [ ! -d "/usr/include/eigen3" ]; then
        print_info "Installing Eigen3..."
        sudo apt-get install -y libeigen3-dev
    else
        print_success "Eigen3 found"
    fi
    
    # Install ROS 2 dependencies
    print_info "Installing ROS 2 dependencies..."
    sudo apt-get install -y \
        ros-humble-gazebo-ros-pkgs \
        ros-humble-rviz2 \
        ros-humble-sensor-msgs \
        ros-humble-nav-msgs \
        ros-humble-geometry-msgs \
        ros-humble-diagnostic-msgs
    
    # Check PX4-Autopilot
    print_info "Checking PX4-Autopilot..."
    if [ ! -d "$HOME/PX4-Autopilot" ]; then
        print_info "PX4-Autopilot not found. Cloning..."
        cd $HOME
        git clone https://github.com/PX4/PX4-Autopilot.git --recursive
        cd PX4-Autopilot
        bash ./Tools/setup/ubuntu.sh
        print_success "PX4-Autopilot installed"
    else
        print_success "PX4-Autopilot found"
    fi
    
    # Check MicroXRCE-DDS Agent
    print_info "Checking MicroXRCE-DDS Agent..."
    if ! check_command "MicroXRCEAgent"; then
        print_info "Installing MicroXRCE-DDS Agent..."
        cd $HOME
        git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git
        cd Micro-XRCE-DDS-Agent
        mkdir build && cd build
        cmake ..
        make
        sudo make install
        sudo ldconfig /usr/local/lib/
        print_success "MicroXRCE-DDS Agent installed"
    fi
    
    print_success "All dependencies installed"
}

###############################################################################
# Build Function
###############################################################################

build_workspace() {
    print_header "Building ROS 2 Workspace"
    
    cd "$PROJECT_DIR"
    
    # Source ROS 2
    source /opt/ros/humble/setup.bash
    
    # Build with colcon
    print_info "Running colcon build..."
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
    
    if [ $? -eq 0 ]; then
        print_success "Build completed successfully"
    else
        print_error "Build failed"
        exit 1
    fi
    
    # Source the workspace
    source install/setup.bash
    print_success "Workspace sourced"
}

###############################################################################
# Launch Function
###############################################################################

launch_simulation() {
    print_header "Launching Indra-Eye SITL Simulation"
    
    cd "$PROJECT_DIR"
    
    # Source workspace
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    
    print_info "Starting simulation stack..."
    print_info "Components:"
    print_info "  - Gazebo (Himalayan terrain)"
    print_info "  - PX4 SITL"
    print_info "  - ES-EKF Node"
    print_info "  - Supervisor Node"
    print_info "  - RViz Visualization"
    
    # Launch using ROS 2 launch file
    ros2 launch indra_eye_sim sitl_launch.py
}

###############################################################################
# Test Function
###############################################################################

run_tests() {
    print_header "Running Validation Tests"
    
    cd "$PROJECT_DIR"
    
    # Source workspace
    source /opt/ros/humble/setup.bash
    source install/setup.bash
    
    print_info "Running unit tests..."
    colcon test --packages-select indra_eye_core indra_eye_supervisor
    
    print_info "Displaying test results..."
    colcon test-result --verbose
    
    print_success "Tests completed"
}

###############################################################################
# Main Script
###############################################################################

print_header "Indra-Eye Setup and Run Script"

case "$1" in
    --install)
        install_dependencies
        build_workspace
        print_success "Installation complete!"
        print_info "Next step: Run 'bash setup_and_run.sh --launch' to start simulation"
        ;;
    
    --launch)
        launch_simulation
        ;;
    
    --test)
        run_tests
        ;;
    
    --build)
        build_workspace
        ;;
    
    *)
        echo "Usage: $0 {--install|--launch|--test|--build}"
        echo ""
        echo "Options:"
        echo "  --install    Install dependencies and build workspace (first-time setup)"
        echo "  --launch     Launch SITL simulation"
        echo "  --test       Run validation tests"
        echo "  --build      Build workspace only"
        echo ""
        echo "Example:"
        echo "  bash setup_and_run.sh --install    # First-time setup"
        echo "  bash setup_and_run.sh --launch     # Launch simulation"
        exit 1
        ;;
esac

exit 0
