#!/bin/bash
echo "🛡️  THE BUILD SHIELD: Forcing clean compilation..."
export MAKEFLAGS="-j4"
rm -rf /tmp/build/build/agri_msgs /tmp/build/install/agri_msgs
source /opt/ros/humble/setup.bash
cd /tmp/build
colcon build --symlink-install
echo "✅ build complete."
