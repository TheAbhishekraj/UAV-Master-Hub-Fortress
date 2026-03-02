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
pkill -f "QGroundControl" 2>/dev/null

docker exec uav_hub_golden bash -c "killall -9 px4 MicroXRCEAgent gz es_ekf_node master_mission_commander ruby python3 px4_msgs 2>/dev/null || true"
docker exec uav_hub_golden bash -c "pkill -9 -f 'ros2' 2>/dev/null || true"
sleep 2

echo "[2/3] Environment purified."
echo "[3/3] Booting Golden Image Terminals..."

# We use gnome-terminal to spawn separate windows automatically.
# This prevents GNOME tab-parsing errors and ensures every tool has dedicated screen space.

echo "[3/4] Launching Master Brain..."
gnome-terminal --title="🧠 Master Brain (Simulation)" -- bash -c "echo -e '\e[1;36m=== MASTER BRAIN LAUNCH ===\e[0m'; xhost +local:docker >/dev/null 2>&1 || true; docker exec -e DISPLAY=\$DISPLAY -e QT_X11_NO_MITSHM=1 uav_hub_golden bash -c 'source /root/startup.sh && source /tmp/fortress_build/install/setup.bash && source /root/uav_master_hub/projects/indra_eye/install/setup.bash && ros2 launch /root/uav_master_hub/projects/indra_eye/src/indra_eye_sim/launch/master_fortress_launch.py'; exec bash" &
sleep 3

echo "[4/4] Launching Supervisor Dashboards..."
gnome-terminal --title="🗺️ Ground Control" -- bash -c "echo -e '\e[1;35m=== STARTING QGROUNDCONTROL ===\e[0m'; /home/abhishek/QGroundControl.AppImage; exec bash" &
gnome-terminal --title="📡 Inner Ear (Diagnostics)" -- bash -c "echo -e '\e[1;33m=== WAITING FOR SIMULATION (15s) ===\e[0m'; sleep 15; echo -e '\e[1;32m=== LISTENING TO INDRA-EYE EKF ===\e[0m'; docker exec uav_hub_golden bash -c 'source /root/startup.sh && ros2 topic echo /indra_eye/diagnostics'; exec bash" &
gnome-terminal --title="🛰️ GPS Denial Trigger (INTERACTIVE)" -- bash -c "echo -e '\e[1;31m=========================================\e[0m'; echo -e '\e[1;31m       🛑 SUPERVISOR OVERRIDE PANEL 🛑\e[0m'; echo -e '\e[1;31m=========================================\e[0m'; echo -e '\n\nDr. Mullick, press [ENTER] at any time during flight to kill the GPS satellites and force the drone to navigate blindly using only the SO(3) Math!\n'; read -p 'Press [ENTER] to inject GPS Denial event... '; echo -e '\e[1;31m>> GPS KILL SIGNAL SENT.\e[0m Check the Inner Ear tab to watch the variance drop!'; docker exec uav_hub_golden bash -c \"source /root/startup.sh && ros2 topic pub -1 /indra_eye/simulate_gps_denial std_msgs/msg/Bool '{data: true}'\"; exec bash" &

echo "✅ DASHBOARD ONLINE!"
echo "Check your screen for the newly opened terminal windows."
