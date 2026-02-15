# Indra-Eye Command Cheatsheet

## 🚀 Quick Start (First Time)

```bash
cd /home/abhishek/Downloads/indra_eye_project
bash setup_and_run.sh --install
```

---

## 🎮 Launch Commands

### SITL Simulation
```bash
# Basic SITL
bash run_mission.sh --sitl

# SITL with QGroundControl
bash run_mission.sh --sitl --qgc

# SITL with recording
bash run_mission.sh --sitl --record

# SITL with everything
bash run_mission.sh --sitl --qgc --record
```

### Hardware-in-the-Loop (HITL)
```bash
# Basic HITL
bash run_mission.sh --hitl

# HITL with QGC
bash run_mission.sh --hitl --qgc

# HITL in Docker
docker-compose -f docker-compose.hitl.yaml up
```

### Master Python Launcher
```bash
# SITL mode
python3 fly.py --mode sitl --qgc --record

# HITL mode
python3 fly.py --mode hitl --qgc

# Validation only
python3 fly.py --validate
```

---

## 🛠️ Build & Maintenance

```bash
# Build workspace
bash setup_and_run.sh --build

# Clean rebuild
rm -rf build/ install/ log/
colcon build --symlink-install

# Kill all processes and restart
bash kill_and_fly.sh

# Validate system
python3 scripts/validate_system.py
```

---

## 📊 ROS 2 Topic Commands

### Monitor ES-EKF Output
```bash
# Fused odometry (100Hz)
ros2 topic echo /indra_eye/fused_odom

# Fused pose with covariance
ros2 topic echo /indra_eye/fused_pose

# Check publishing rate
ros2 topic hz /indra_eye/fused_odom
```

### Check Navigation Mode
```bash
# Current mode (GNSS/VIO/SLAM/EMERGENCY)
ros2 topic echo /indra_eye/navigation_mode

# Spoofing detection status
ros2 topic echo /indra_eye/spoofing_detected
```

### View Diagnostics
```bash
# ES-EKF diagnostics (1Hz)
ros2 topic echo /indra_eye/diagnostics

# Sensor update rates
ros2 topic echo /indra_eye/diagnostics | grep "update_rate"
```

### Sensor Data
```bash
# IMU (400Hz)
ros2 topic hz /px4/imu
ros2 topic echo /px4/imu

# GNSS (10Hz)
ros2 topic hz /px4/gnss
ros2 topic echo /px4/gnss

# VIO (30Hz)
ros2 topic hz /camera/stereo/odom
ros2 topic echo /camera/stereo/odom

# SLAM (10Hz)
ros2 topic hz /lidar/slam/pose
ros2 topic echo /lidar/slam/pose
```

### Visualization Paths
```bash
# GPS path (red)
ros2 topic echo /visualization/gps_path

# VIO path (blue)
ros2 topic echo /visualization/vio_path

# SLAM path (cyan)
ros2 topic echo /visualization/slam_path

# Fused path (green)
ros2 topic echo /visualization/fused_path
```

---

## 🧪 Testing Commands

### Trigger GPS Denial
```bash
# Enable GPS denial
ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool "data: true"

# Disable GPS denial
ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool "data: false"
```

### Manual Sensor Injection
```bash
# Publish fake GNSS
ros2 topic pub /px4/gnss sensor_msgs/NavSatFix "{latitude: 34.1526, longitude: 77.5771, altitude: 3500.0}"

# Publish fake VIO
ros2 topic pub /camera/stereo/odom nav_msgs/Odometry "{pose: {pose: {position: {x: 0, y: 0, z: 0}}}}"
```

---

## 📈 Data Analysis

### Record Mission
```bash
# Record all topics
ros2 bag record -a -o mission_$(date +%Y%m%d_%H%M%S)

# Record specific topics
ros2 bag record \
  /indra_eye/fused_odom \
  /indra_eye/navigation_mode \
  /px4/gnss \
  /camera/stereo/odom \
  -o mission_data
```

### Play Back Recording
```bash
# Play bag
ros2 bag play mission_data.bag

# Play at 0.5x speed
ros2 bag play mission_data.bag --rate 0.5

# Play specific topics
ros2 bag play mission_data.bag --topics /indra_eye/fused_odom
```

### Plot Trajectories
```bash
# Generate PhD thesis plot
python3 scripts/plot_trajectories.py \
  --bag logs/rosbags/mission_20260215.bag \
  --output thesis_figure_1.png
```

### Calculate RMSE
```bash
# Compare against ground truth
python3 scripts/calculate_rmse.py \
  --bag logs/rosbags/mission.bag \
  --ground_truth rtk_data.csv \
  --output rmse_report.txt
```

---

## 🔍 Debugging

### Check All Topics
```bash
ros2 topic list | grep indra_eye
```

### Check Node Status
```bash
# List running nodes
ros2 node list

# Node info
ros2 node info /es_ekf_node
ros2 node info /supervisor_node
ros2 node info /mavros_bridge_node
```

### Check Parameters
```bash
# List parameters
ros2 param list /es_ekf_node

# Get parameter value
ros2 param get /es_ekf_node use_gnss

# Set parameter
ros2 param set /es_ekf_node publish_rate_hz 100.0
```

### View TF Tree
```bash
# View transforms
ros2 run tf2_tools view_frames

# Echo specific transform
ros2 run tf2_ros tf2_echo map base_link
```

---

## 🚨 Emergency Commands

### Kill All Processes
```bash
# Nuclear option
killall -9 gazebo gzserver gzclient px4 MicroXRCEAgent mavros rviz2 qgroundcontrol

# Kill ROS 2 processes
pkill -9 -f "ros2 launch"
pkill -9 -f "indra_eye"
```

### Check Port Usage
```bash
# MAVLink ports
netstat -tulpn | grep 14550
netstat -tulpn | grep 14557

# DDS port
netstat -tulpn | grep 8888

# Kill process on port
fuser -k 14550/udp
```

### Reset PX4
```bash
# In PX4 console
reboot

# Or kill and restart
killall -9 px4
cd ~/PX4-Autopilot
make px4_sitl gazebo
```

---

## 📦 Docker Commands

### Build Image
```bash
docker build -t indra_eye:latest .
```

### Run Container
```bash
# Interactive
docker run -it --rm \
  --privileged \
  --network host \
  -v /home/abhishek/Downloads/indra_eye_project:/workspace \
  -e DISPLAY=$DISPLAY \
  indra_eye:latest

# Using Docker Compose
docker-compose -f docker-compose.hitl.yaml up
docker-compose -f docker-compose.hitl.yaml down
```

### Container Management
```bash
# List containers
docker ps -a

# Stop container
docker stop indra_eye_hitl

# Remove container
docker rm indra_eye_hitl

# View logs
docker logs indra_eye_hitl
```

---

## 🔧 PX4 Commands

### Upload Parameters
```bash
ros2 run mavros mavparam load config/px4_params_indra_eye.txt
```

### Check PX4 Status
```bash
# Via MAVROS
ros2 topic echo /mavros/state

# In PX4 console
commander status
ekf2 status
```

### Arm/Disarm
```bash
# Arm
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: true}"

# Disarm
ros2 service call /mavros/cmd/arming mavros_msgs/srv/CommandBool "{value: false}"
```

### Set Mode
```bash
# Position hold
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'POSCTL'}"

# Return to launch
ros2 service call /mavros/set_mode mavros_msgs/srv/SetMode "{custom_mode: 'RTL'}"
```

---

## 📝 Log Management

### View Logs
```bash
# ROS 2 logs
cat ~/.ros/log/latest/indra_eye_core/es_ekf_node-*.log

# PX4 logs
ls ~/PX4-Autopilot/build/px4_sitl_default/logs/

# System logs
journalctl -u indra_eye
```

### Clean Logs
```bash
# Remove old ROS logs
rm -rf ~/.ros/log/*

# Remove old bags
rm -rf logs/rosbags/*

# Remove PX4 logs
rm -rf ~/PX4-Autopilot/build/px4_sitl_default/logs/*
```

---

## 🎓 PhD Workflow

### Collect Data
```bash
# 20-minute flight with recording
python3 fly.py --mode sitl --duration 1200 --record --output thesis_data_1
```

### Generate Figures
```bash
# Trajectory comparison
python3 scripts/plot_trajectories.py --bag thesis_data_1.bag --output fig_1_trajectories.png

# Error analysis
python3 scripts/plot_errors.py --bag thesis_data_1.bag --output fig_2_errors.png

# Covariance evolution
python3 scripts/plot_covariance.py --bag thesis_data_1.bag --output fig_3_covariance.png
```

### Extract Statistics
```bash
# Generate LaTeX table
python3 scripts/generate_stats_table.py --bag thesis_data_1.bag --output table_1.tex
```

---

## 🌐 Network Commands (HITL)

### Configure Livox LiDAR Network
```bash
# Set static IP
sudo ifconfig eth0 192.168.1.100 netmask 255.255.255.0 up

# Add route
sudo route add -net 192.168.1.0 netmask 255.255.255.0 dev eth0

# Ping LiDAR
ping 192.168.1.10
```

### Check Sensor Connectivity
```bash
# RealSense
rs-enumerate-devices

# u-blox GNSS
ls /dev/ttyUSB*
cat /dev/ttyUSB0

# Livox
ping 192.168.1.10
```

---

## 📚 Documentation

### Generate Doxygen
```bash
cd docs
doxygen Doxyfile
firefox html/index.html
```

### Build LaTeX Thesis
```bash
cd docs/thesis
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

---

## 🔑 Key File Locations

```
Config Files:       /home/abhishek/Downloads/indra_eye_project/config/
Launch Files:       /home/abhishek/Downloads/indra_eye_project/src/indra_eye_sim/launch/
Logs:               /home/abhishek/Downloads/indra_eye_project/logs/
ROS Bags:           /home/abhishek/Downloads/indra_eye_project/logs/rosbags/
Scripts:            /home/abhishek/Downloads/indra_eye_project/scripts/
Documentation:      /home/abhishek/Downloads/indra_eye_project/docs/
Manual:             /home/abhishek/Downloads/indra_eye_project/INDRA_EYE_MANUAL.md
```

---

## 💡 Pro Tips

1. **Always source workspace**: `source install/setup.bash`
2. **Check topic rates**: `ros2 topic hz <topic>` to verify sensor data
3. **Use RViz for debugging**: Visual feedback is invaluable
4. **Record everything**: Disk is cheap, lost data is expensive
5. **Monitor diagnostics**: `/indra_eye/diagnostics` shows filter health
6. **Test GPS denial gradually**: Start with 10s, then 30s, then 60s
7. **Keep QGC open**: Real-time telemetry helps catch issues early
8. **Backup rosbags**: Copy to external drive after each flight

---

**🇮🇳 Jai Hind! 🇮🇳**
