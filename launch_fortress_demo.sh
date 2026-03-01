#!/bin/bash

# =========================================================================
# 🦅 UAV Master Hub - Golden Demo Launcher (Supervisor Demo Script)
# =========================================================================
# This script spins up a multi-tab terminal dashboard using gnome-terminal
# to perfectly orchestrate the Ph.D. SITL Drone simulation and diagnostics.
# =========================================================================

echo "========================================="
echo "🦅 INITIATING MULTI-TERMINAL DASHBOARD..."
echo "========================================="

echo "[1/3] Scrubbing any old, stale background processes (Host & Container)..."
pkill -f "docker exec uav_hub_golden" 2>/dev/null
pkill -f "docker exec -it uav_hub_golden" 2>/dev/null

docker exec uav_hub_golden bash -c "killall -9 px4 MicroXRCEAgent gz es_ekf_node master_mission_commander ruby python3 px4_msgs" 2>/dev/null
sleep 2

echo "[2/3] Environment purified."
echo "[3/3] Booting Golden Image Terminals..."

# We use gnome-terminal to spawn tabs automatically.
# The user doesn't need to manually open 3 windows anymore!
gnome-terminal \
  --window --title="🦅 UAV Master Dashboard" \
  --tab --title="🧠 Master Brain (Simulation)" \
    -- bash -c "echo -e '\e[1;36m=== MASTER BRAIN LAUNCH ===\e[0m'; docker exec -it uav_hub_golden bash -c 'source /root/startup.sh && source /tmp/fortress_build/install/setup.bash && source /root/uav_master_hub/projects/indra_eye/install/setup.bash && ros2 launch /root/uav_master_hub/projects/indra_eye/src/indra_eye_sim/launch/master_fortress_launch.py'; exec bash" \
  --tab --title="📡 Inner Ear (Diagnostics)" \
    -- bash -c "echo -e '\e[1;33m=== WAITING FOR SIMULATION (15s) ===\e[0m'; sleep 15; echo -e '\e[1;32m=== LISTENING TO INDRA-EYE EKF ===\e[0m'; docker exec -it uav_hub_golden bash -c 'source /root/startup.sh && ros2 topic echo /indra_eye/diagnostics'; exec bash" \
  --tab --title="🛰️ GPS Denial Trigger (INTERACTIVE)" \
    -- bash -c "echo -e '\e[1;31m=========================================\e[0m'; echo -e '\e[1;31m       🛑 SUPERVISOR OVERRIDE PANEL 🛑\e[0m'; echo -e '\e[1;31m=========================================\e[0m'; echo -e '\n\nDr. Mullick, press [ENTER] at any time during flight to kill the GPS satellites and force the drone to navigate blindly using only the SO(3) Math!\n'; read -p 'Press [ENTER] to inject GPS Denial event... '; echo -e '\e[1;31m>> GPS KILL SIGNAL SENT.\e[0m Check the Inner Ear tab to watch the variance drop!'; docker exec -it uav_hub_golden bash -c \"source /root/startup.sh && ros2 topic pub -1 /indra_eye/simulate_gps_denial std_msgs/msg/Bool '{data: true}'\"; exec bash"

echo "✅ DASHBOARD ONLINE!"
echo "Please switch to the newly opened terminal window."
