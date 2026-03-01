#!/bin/bash
# restore_demo.sh - Emergency recovery for Prof. Mullick's Demo
# Restores the Hexacopter + Bihar Farm simulation via Split-Launch

# 1. Cleanup
docker exec uav_hub_golden bash -c "pkill -9 -f gazebo; pkill -9 -f px4; pkill -9 -f ros; pkill -9 -f rviz; sleep 2"

# 2. Start GZ Server
docker exec -d uav_hub_golden bash -c "export GZ_SIM_RESOURCE_PATH=/root/uav_master_hub/assets/models:/root/uav_master_hub/assets/worlds:/root/PX4-Autopilot/Tools/simulation/gz/models && gz sim -s -r /root/PX4-Autopilot/Tools/simulation/gz/worlds/bihar_maize.sdf"
sleep 10

# 3. Spawn Drone
docker exec uav_hub_golden gz service -s /world/bihar_maize/create --reqtype gz.msgs.EntityFactory --reptype gz.msgs.Boolean --timeout 10000 --req "sdf_filename: '/root/uav_master_hub/assets/models/agri_hexacopter_drone/model.sdf', name: 'agri_hexacopter_drone', pose: {position: {z: 0.5}}"

# 4. Start PX4
docker exec -d uav_hub_golden bash -c "export PX4_GZ_STANDALONE=1 && export PX4_GZ_WORLD=bihar_maize && export PX4_GZ_MODEL=agri_hexacopter_drone && cd /root/PX4-Autopilot && make px4_sitl gz_standard_vtol"

# 5. Start GUI
docker exec -d uav_hub_golden bash -c "export DISPLAY=:0 && export QT_X11_NO_MITSHM=1 && gz sim -g"

echo "Demo Restoration Triggered. Check the Gazebo Window in 30 seconds."
