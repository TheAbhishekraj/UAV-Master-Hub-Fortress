# Multi-Terminal Launch Scripts

## Overview

Two launch scripts for running Indra-Eye with multiple terminal windows/panes:

1. **launch_multi_terminal.sh** - Multiple separate terminal windows (GUI)
2. **launch_tmux.sh** - Single window with multiple panes (tmux)

---

## Option 1: Multiple Terminal Windows (Recommended for GUI)

### Usage

```bash
cd /home/abhishek/Downloads/indra_eye_project
bash launch_multi_terminal.sh
```

### Terminal Layout

```
┌─────────────────────┬─────────────────────┐
│  Terminal 1         │  Terminal 2         │
│  Gazebo + PX4 SITL  │  ES-EKF + Supervisor│
│                     │                     │
├─────────────────────┼─────────────────────┤
│  Terminal 3         │  Terminal 4         │
│  MAVROS + DDS       │  RViz Visualization │
│                     │                     │
└─────────────────────┴─────────────────────┘
         ┌─────────────────────┐
         │  Terminal 5         │
         │  Mission Monitor    │
         │  & Control          │
         └─────────────────────┘
              + QGroundControl (separate window)
```

### What Each Terminal Does

**Terminal 1: Gazebo + PX4 SITL**
- Launches Gazebo simulator with Himalayan terrain
- Starts PX4 SITL autopilot
- Shows Gazebo GUI and PX4 console output

**Terminal 2: ES-EKF + Supervisor**
- Runs ES-EKF node (sensor fusion at 100Hz)
- Runs Supervisor node (spoofing detection)
- Shows filter diagnostics and mode transitions

**Terminal 3: MAVROS + DDS Agent**
- Starts Micro-XRCE-DDS Agent (ROS 2 ↔ PX4 bridge)
- Runs MAVROS node (MAVLink communication)
- Runs MAVROS Bridge (ES-EKF → QGC telemetry)
- Runs Path Aggregator (multi-path visualization)

**Terminal 4: RViz**
- Launches RViz with custom configuration
- Shows 4 trajectories: GPS (red), VIO (blue), SLAM (cyan), Fused (green)
- Displays current pose and uncertainty ellipsoid

**Terminal 5: Mission Monitor**
- Central control terminal
- Shows quick status and available commands
- Use this for testing GPS denial and monitoring

**QGroundControl**
- Separate window for GCS telemetry
- Shows custom dashboard with sensor health
- Displays spoofing alerts

---

## Option 2: TMux Multi-Pane (Recommended for SSH/Remote)

### Usage

```bash
cd /home/abhishek/Downloads/indra_eye_project
bash launch_tmux.sh
```

### Pane Layout

```
┌──────────────────────┬──────────────────────┐
│  Pane 1              │  Pane 2              │
│  Gazebo + PX4        │  ES-EKF + Supervisor │
│                      │                      │
├──────────────────────┼──────────────────────┤
│  Pane 3              │  Pane 4              │
│  MAVROS + DDS        │  Mission Monitor     │
│                      │                      │
└──────────────────────┴──────────────────────┘
```

### TMux Controls

| Action | Command |
|--------|---------|
| Navigate panes | `Ctrl+B` then arrow keys |
| Scroll mode | `Ctrl+B` then `[` (press `q` to exit) |
| Detach session | `Ctrl+B` then `d` |
| Reattach | `tmux attach -t indra_eye_mission` |
| Kill window | `Ctrl+B` then `&` |
| Zoom pane | `Ctrl+B` then `z` (toggle) |

---

## Initialization Timeline

| Time | Event |
|------|-------|
| 0s | Launch script starts, kills old processes |
| 3s | Gazebo + PX4 SITL starts |
| 10s | ES-EKF + Supervisor start |
| 12s | MAVROS + DDS Agent start |
| 15s | RViz starts |
| 18s | Path Aggregator starts |
| 20s | QGroundControl launches |
| 30s | **All systems ready** |

---

## Testing GPS Denial

**In Terminal 5 (Mission Monitor) or any terminal:**

```bash
# Enable GPS denial
ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool "data: true"

# Wait 30 seconds, observe:
# - QGC: "⚠ VIO Mode - GPS Denied"
# - RViz: GPS path (red) jumps, Fused path (green) smooth
# - Terminal 2: Mode change logged

# Restore GPS
ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool "data: false"
```

---

## Monitoring Commands

### Check All Topics
```bash
ros2 topic list | grep indra_eye
```

### Monitor Diagnostics
```bash
ros2 topic echo /indra_eye/diagnostics
```

### Check Navigation Mode
```bash
ros2 topic echo /indra_eye/navigation_mode
```

### View Sensor Rates
```bash
ros2 topic hz /px4/imu              # Should be 400Hz
ros2 topic hz /indra_eye/fused_odom # Should be 100Hz
ros2 topic hz /px4/gnss             # Should be 10Hz
```

### Check MAVROS Connection
```bash
ros2 topic echo /mavros/state
```

---

## Stopping the System

### Graceful Shutdown
Press `Ctrl+C` in each terminal window

### Force Kill All
```bash
killall -9 gazebo gzserver gzclient px4 MicroXRCEAgent mavros rviz2 qgroundcontrol
```

### Kill TMux Session
```bash
tmux kill-session -t indra_eye_mission
```

---

## Troubleshooting

### Issue: Terminals fail to launch
**Solution**: Build workspace first
```bash
bash setup_and_run.sh --build
```

### Issue: QGroundControl not found
**Solution**: Install QGC
```bash
sudo apt install qgroundcontrol
# Or download from: https://docs.qgroundcontrol.com/
```

### Issue: Gazebo black screen
**Solution**: Software rendering
```bash
export LIBGL_ALWAYS_SOFTWARE=1
bash launch_multi_terminal.sh
```

### Issue: Port already in use
**Solution**: Kill processes on ports
```bash
fuser -k 14550/udp
fuser -k 14557/udp
fuser -k 8888/udp
```

### Issue: TMux session already exists
**Solution**: Kill old session
```bash
tmux kill-session -t indra_eye_mission
bash launch_tmux.sh
```

---

## Comparison: Multi-Terminal vs TMux

| Feature | Multi-Terminal | TMux |
|---------|----------------|------|
| **GUI Required** | Yes | No |
| **SSH Friendly** | No | Yes |
| **Window Management** | Separate windows | Single window, multiple panes |
| **Scrollback** | Native terminal | `Ctrl+B` then `[` |
| **Detach/Reattach** | No | Yes |
| **Screen Real Estate** | More flexible | More compact |
| **Best For** | Local development | Remote/SSH sessions |

---

## Advanced Usage

### Record Mission in TMux
```bash
# In Mission Monitor pane
ros2 bag record -a -o mission_$(date +%Y%m%d_%H%M%S)
```

### Split Additional Pane in TMux
```bash
# Horizontal split
Ctrl+B then "

# Vertical split
Ctrl+B then %
```

### Resize Panes in TMux
```bash
# Hold Ctrl+B, then use arrow keys while holding Ctrl
Ctrl+B then Ctrl+Arrow
```

---

## Next Steps

1. **First Launch**: Use `launch_multi_terminal.sh` for visual feedback
2. **Monitor**: Watch all terminals for 30 seconds during initialization
3. **Test**: Trigger GPS denial and observe mode transitions
4. **Record**: Use `--record` flag or manual rosbag recording
5. **Analyze**: Plot trajectories with `scripts/plot_trajectories.py`

---

**🇮🇳 Jai Hind! 🇮🇳**
