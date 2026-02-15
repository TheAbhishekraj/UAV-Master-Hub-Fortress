#!/bin/bash
# Indra-Eye Dependency Installer & Fixer
# Installs ROS 2 Humble, Colcon, and QGroundControl

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Indra-Eye System Repair & Install${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. Check for ROS 2 Humble
if [ ! -f /opt/ros/humble/setup.bash ]; then
    echo -e "${RED}[MISSING] ROS 2 Humble not found.${NC}"
    echo "Installing ROS 2 Humble..."
    
    sudo apt update && sudo apt install -y software-properties-common
    sudo add-apt-repository universe -y
    sudo apt update && sudo apt install -y curl gnupg2 lsb-release
    
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
    
    sudo apt update
    sudo apt install -y ros-humble-desktop
    sudo apt install -y ros-dev-tools
else
    echo -e "${GREEN}[OK] ROS 2 Humble found.${NC}"
fi

# 2. Check for Colcon
if ! command -v colcon &> /dev/null; then
    echo -e "${RED}[MISSING] Colcon build tool not found.${NC}"
    echo "Installing python3-colcon-common-extensions..."
    sudo apt install -y python3-colcon-common-extensions
else
    echo -e "${GREEN}[OK] Colcon found.${NC}"
fi

# 3. Check for QGroundControl
if ! command -v qgroundcontrol &> /dev/null; then
    echo -e "${RED}[MISSING] QGroundControl not found.${NC}"
    echo "Installing QGroundControl..."
    
    sudo usermod -a -G dialout $USER
    sudo apt-get remove modemmanager -y
    sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
    sudo apt install libqt5gui5 -y
    sudo apt install libfuse2 -y

    wget https://d176tv9ibo4jval4.cloudfront.net/latest/QGroundControl.AppImage
    chmod +x QGroundControl.AppImage
    sudo mv QGroundControl.AppImage /usr/local/bin/qgroundcontrol
    
    echo -e "${GREEN}QGroundControl installed to /usr/local/bin/qgroundcontrol${NC}"
else
    echo -e "${GREEN}[OK] QGroundControl found.${NC}"
fi

# 4. Fix Workspace Build
echo -e "${GREEN}Verifying Workspace Build...${NC}"
if [ ! -f "install/setup.bash" ]; then
    echo -e "${RED}Workspace not built.${NC}"
    source /opt/ros/humble/setup.bash
    colcon build --symlink-install
else
   echo -e "${GREEN}[OK] Workspace appears built.${NC}"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}System Check Complete. Ready to Launch!${NC}"
echo -e "${GREEN}========================================${NC}"
