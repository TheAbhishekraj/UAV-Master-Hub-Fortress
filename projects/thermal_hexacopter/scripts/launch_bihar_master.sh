#!/usr/bin/env bash
# =============================================================================
# launch_bihar_master.sh - The Definitive Ignition Script for Bihar Mission
# =============================================================================

echo "🧹 CLEANUP: Terminating stale processes..."
pkill -9 gz || true
pkill -9 px4 || true
pkill -9 MicroXRCEAgent || true
pkill -9 -f 'ros2' || true
sleep 2

echo "🌍 PHASE 1: The World & The Body (PX4 + Gazebo)"
export DISPLAY=:0
export PX4_GZ_WORLD=bihar_maize
export PX4_GZ_MODEL=agri_hexacopter_drone
export PX4_HOME_LAT=25.344644
export PX4_HOME_LON=86.483958
export GZ_SIM_RESOURCE_PATH=/root/uav_master_hub/assets/models:/root/uav_master_hub/assets/worlds:${GZ_SIM_RESOURCE_PATH}

cd /root/PX4-Autopilot
mkdir -p /tmp/mavlink_logs
nohup make px4_sitl gz_x500 > /tmp/mavlink_logs/px4.log 2>&1 &
echo "⏳ Waiting 20 seconds for Gazebo to initialize..."
sleep 20

echo "🌉 PHASE 2: The Nervous System (MicroXRCEAgent)"
nohup MicroXRCEAgent udp4 -p 8888 > /tmp/mavlink_logs/dds.log 2>&1 &
echo "⏳ Waiting 5 seconds for DDS bridge..."
sleep 5

echo "🧠 PHASE 3: The Super Brain (ROS 2 Autonomy Nodes)"
source /opt/ros/humble/setup.bash
source /tmp/build/install/setup.bash
nohup ros2 launch agri_hexacopter full_autonomy.launch.py use_sim_time:=false > /tmp/mavlink_logs/ros2.log 2>&1 &

echo "📺 PHASE 4: The Monitor (Mission Log)"
echo "Targeting /agri/mission/log..."
sleep 3
ros2 topic echo /agri/mission/log
