#!/bin/bash
###############################################################################
# Indra-Eye: TMux-Based Multi-Pane Launcher
#
# Alternative launcher using tmux for a single window with multiple panes.
# Better for systems without GUI or for remote SSH sessions.
#
# Usage:
#   bash launch_tmux.sh
#
# Controls:
#   Ctrl+B then arrow keys - Navigate between panes
#   Ctrl+B then [ - Scroll mode (q to exit)
#   Ctrl+B then d - Detach (tmux attach to reattach)
#   Ctrl+B then & - Kill window
#
# Author: Indra-Eye Development Team
# License: MIT
###############################################################################

set -e

PROJECT_DIR="/home/abhishek/thermal_hexacopter_project"
SESSION_NAME="indra_eye_mission"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux not found. Installing..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# Kill existing session if it exists
tmux kill-session -t $SESSION_NAME 2>/dev/null || true

# Kill existing processes
killall -9 gazebo gzserver gzclient px4 MicroXRCEAgent mavros rviz2 2>/dev/null || true
sleep 2

echo "========================================="
echo "Indra-Eye TMux Multi-Pane Launcher"
echo "========================================="
echo ""
echo "Creating tmux session: $SESSION_NAME"
echo ""

# Create new session with first pane
tmux new-session -d -s $SESSION_NAME -n "Indra-Eye" -c "$PROJECT_DIR"

# Pane 0: Gazebo + PX4 SITL (top-left)
tmux send-keys -t $SESSION_NAME:0.0 "
cd $PROJECT_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null || echo 'Workspace not built'
echo '========================================='
echo 'Pane 1: Gazebo + PX4 SITL'
echo '========================================='
sleep 3
ros2 launch indra_eye_sim sitl_launch.py use_rviz:=false use_qgc:=false
" C-m

# Split horizontally (create pane 1: top-right)
tmux split-window -h -t $SESSION_NAME:0 -c "$PROJECT_DIR"

# Pane 1: ES-EKF + Supervisor (top-right)
tmux send-keys -t $SESSION_NAME:0.1 "
cd $PROJECT_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null || echo 'Workspace not built'
echo '========================================='
echo 'Pane 2: ES-EKF + Supervisor'
echo '========================================='
sleep 10
echo 'Launching ES-EKF...'
ros2 run indra_eye_core es_ekf_node &
sleep 2
echo 'Launching Supervisor...'
ros2 run indra_eye_supervisor supervisor_node &
echo 'Core nodes running!'
bash
" C-m

# Split pane 0 vertically (create pane 2: bottom-left)
tmux split-window -v -t $SESSION_NAME:0.0 -c "$PROJECT_DIR"

# Pane 2: MAVROS + DDS (bottom-left)
tmux send-keys -t $SESSION_NAME:0.2 "
cd $PROJECT_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null || echo 'Workspace not built'
echo '========================================='
echo 'Pane 3: MAVROS + DDS Agent'
echo '========================================='
sleep 12
echo 'Starting Micro-XRCE-DDS Agent...'
MicroXRCEAgent udp4 -p 8888 &
sleep 2
echo 'Starting MAVROS...'
ros2 run mavros mavros_node --ros-args -p fcu_url:=udp://:14540@127.0.0.1:14557 &
sleep 2
echo 'Starting MAVROS Bridge...'
ros2 run indra_eye_core mavros_bridge_node &
sleep 1
echo 'Starting Path Aggregator...'
ros2 run indra_eye_core path_aggregator_node &
echo 'Communication nodes running!'
bash
" C-m

# Split pane 1 vertically (create pane 3: bottom-right)
tmux split-window -v -t $SESSION_NAME:0.1 -c "$PROJECT_DIR"

# Pane 3: Mission Monitor (bottom-right)
tmux send-keys -t $SESSION_NAME:0.3 "
cd $PROJECT_DIR
source /opt/ros/humble/setup.bash
source install/setup.bash 2>/dev/null || echo 'Workspace not built'
echo '========================================='
echo 'Pane 4: Mission Monitor & Control'
echo '========================================='
sleep 18
echo ''
echo '✅ All systems ready!'
echo ''
echo '📊 Quick Commands:'
echo ''
echo '  # Test GPS Denial'
echo '  ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool \"data: true\"'
echo ''
echo '  # Monitor Diagnostics'
echo '  ros2 topic echo /indra_eye/diagnostics'
echo ''
echo '  # Check Navigation Mode'
echo '  ros2 topic echo /indra_eye/navigation_mode'
echo ''
echo '  # View Topics'
echo '  ros2 topic list | grep indra_eye'
echo ''
echo '🎮 TMux Controls:'
echo '  Ctrl+B then arrow keys - Navigate panes'
echo '  Ctrl+B then [ - Scroll mode (q to exit)'
echo '  Ctrl+B then d - Detach session'
echo '  Ctrl+B then & - Kill window'
echo ''
bash
" C-m

# Balance panes
tmux select-layout -t $SESSION_NAME:0 tiled

echo ""
echo "✅ TMux session created!"
echo ""
echo "Attaching to session in 3 seconds..."
echo ""
echo "TMux Quick Reference:"
echo "  Ctrl+B then arrow keys - Navigate between panes"
echo "  Ctrl+B then [          - Scroll mode (press 'q' to exit)"
echo "  Ctrl+B then d          - Detach (run 'tmux attach -t $SESSION_NAME' to reattach)"
echo "  Ctrl+B then &          - Kill entire window"
echo ""

sleep 3

# Attach to session
tmux attach-session -t $SESSION_NAME
