#!/bin/bash
# --- PHASE 1: FIX THE MODEL PATH ---
# We are creating a link from your root models folder into your ROS package
# so Gazebo never loses the drone.
cd ~/thermal_hexacopter_project/workspace
ln -s $(pwd)/models/agri_hexacopter_drone src/agri_hexacopter/models/

# --- PHASE 2: LAUNCH THE LAB ---
xhost +local:docker
docker run -it --privileged --network=host \
 --env="DISPLAY=$DISPLAY" \
 --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
 -v ~/thermal_hexacopter_project/workspace:/root/hexacopter_phd \
 hexacopter_lab_final
