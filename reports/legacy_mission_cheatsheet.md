# 🚁 Mission Command Cheatsheet - Bihar Maiden Voyage

**Quick Reference Guide for Complete PhD Mission Execution**

---

## 📋 Pre-Flight Checklist

- [ ] Docker installed and running
- [ ] X11 forwarding enabled (`xhost +local:docker`)
- [ ] Project directory: `~/thermal_hexacopter_project`
- [ ] Container image: `hexacopter_lab_safe_copy`
- [ ] Display available: `echo $DISPLAY` (should show `:0` or similar)

---

## 🎬 STEP 1: Start Screen Recording (Host Terminal)

**Purpose:** Capture 1920x1080 HD video of entire mission for supervisor presentation

**Command:**
```bash
ffmpeg -video_size 1920x1080 -framerate 30 \
  -f x11grab -i :0.0 \
  -c:v libx264 -preset ultrafast -crf 18 \
  bihar_maiden_voyage_$(date +%Y%m%d_%H%M%S).mp4
```

**Expected Output:**
```
Input #0, x11grab, from ':0.0':
  Duration: N/A, start: 1707945825.123456, bitrate: N/A
  Stream #0:0: Video: rawvideo, bgra, 1920x1080, 30 fps
Output #0, mp4, to 'bihar_maiden_voyage_20260215_004000.mp4':
  Stream #0:0: Video: h264, yuv420p, 1920x1080, q=2-31, 30 fps
frame=    1 fps=0.0 q=0.0 size=       0kB time=00:00:00.03 bitrate=   0.0kbits/s
```

**Status Indicator:** Frame counter incrementing (e.g., `frame= 120 fps=30.0`)

**To Stop:** Press `Ctrl+C` when mission completes

**Output File:** `bihar_maiden_voyage_YYYYMMDD_HHMMSS.mp4` in current directory

---

## 🚀 STEP 2: Launch Bihar World Simulation (Terminal 1)

**Purpose:** Start Gazebo with Bihar maize farm and hexacopter model

**Command:**
```bash
cd ~/thermal_hexacopter_project
xhost +local:docker
docker run -it --rm --privileged --network=host \
    -e DISPLAY=$DISPLAY \
    -e LIBGL_ALWAYS_SOFTWARE=1 \
    -e QT_X11_NO_MITSHM=1 \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd)/workspace:/root/workspace \
    -v $(pwd)/scripts:/root/scripts \
    --name hexacopter_gui \
    hexacopter_lab_safe_copy \
    -c "cd /root/workspace && chmod +x ../scripts/visual_hexacopter_bihar.sh && ../scripts/visual_hexacopter_bihar.sh"
```

**Expected Output:**
```
🌾 BIHAR MISSION: High-Fidelity Agricultural Simulation
==================================================
📦 Sourcing ROS 2 Humble...
🔌 Starting MicroXRCEAgent...
🗺️  Configuring Gazebo resource paths...
🚁 Configuring PX4 for hexacopter...
📍 Setting Bihar GPS coordinates...
🌾 Loading Bihar Maize Farm World...
🚀 Launching PX4 SITL with Bihar World...

INFO  [simulator_mavlink] Waiting for simulator to accept connection on TCP port 4560
INFO  [gz_bridge] Creating GZ bridge for world [bihar_maize_farm]
```

**Visual Confirmation:**
- Gazebo window opens
- Green maize field with 30cm row spacing
- Red landing pad at center
- Hexacopter model sitting on pad
- Sky and sun visible

**Container Name:** `hexacopter_gui` (for subsequent commands)

---

## 🧠 STEP 3: Start Thermal AI Monitor (Terminal 2)

**Purpose:** Launch MobileNetV2 disease detection node (91.9% F1-score)

**Command:**
```bash
docker exec hexacopter_gui /bin/bash -c \
    "source /opt/ros/humble/setup.bash && \
     source /root/workspace/install/setup.bash && \
     ros2 run agri_hexacopter thermal_monitor"
```

**Expected Output:**
```
[INFO] [thermal_monitor]: Thermal Monitor Node Started
[INFO] [thermal_monitor]: Subscribed to /agri/thermal/image_raw
[INFO] [thermal_monitor]: Publishing alerts to /agri/crop_health/alerts
[INFO] [thermal_monitor]: MobileNetV2 model loaded (3.4M parameters)
[INFO] [thermal_monitor]: Inference latency: 45ms (22 fps throughput)
```

**Status Indicator:** Node running, waiting for thermal images

**Disease Alert Format:**
```
🚨 DISEASE HOTSPOT DETECTED
Frame: 45 | Confidence: 78.3%
Cluster Size: 127 px | Location: (320, 240)
GPS: [25.344644, 86.483958]
Total Detections: 1
```

---

## 🎯 STEP 4: Execute Survey Mission (Terminal 3)

**Purpose:** Launch Level 3 autonomous zig-zag survey pattern

**Command:**
```bash
docker exec hexacopter_gui /bin/bash -c \
    "source /opt/ros/humble/setup.bash && \
     source /root/workspace/install/setup.bash && \
     /root/workspace/install/agri_bot_missions/bin/level3_survey"
```

**Expected Output:**
```
[INFO] Starting Level 3 Survey Mission
[INFO] Target waypoints: 7
[INFO] Survey altitude: 5.0m
[INFO] Coverage area: 10m × 8m (80m²)
[INFO] Arming vehicle...
[INFO] Vehicle armed successfully
[INFO] Taking off to 5.0m...
[INFO] Reached waypoint 1/7
[INFO] Reached waypoint 2/7
...
[INFO] Reached waypoint 7/7
[INFO] Returning to home...
[INFO] Landing...
[INFO] Mission complete! Duration: 95 seconds
```

**Mission Timeline:**
- 0-5s: Arm and takeoff
- 5-57s: Waypoint navigation (7 points)
- 57-95s: Return-to-home and landing

**Success Criteria:**
- ✅ 7/7 waypoints completed
- ✅ Altitude hold: ±0.06m
- ✅ Thermal alerts generated
- ✅ Safe landing on pad

---

## 📊 STEP 5: Monitor Telemetry (Optional - Terminal 4)

**Purpose:** Real-time position tracking for validation

**Command:**
```bash
docker exec hexacopter_gui /bin/bash -c \
    "source /opt/ros/humble/setup.bash && \
     source /root/workspace/install/setup.bash && \
     ros2 topic echo /fmu/out/vehicle_local_position --field z"
```

**Expected Output:**
```
-4.94
-4.95
-4.93
-4.96
```

**Interpretation:** Negative Z values (NED coordinates), target: -5.0m

---

## 🛑 STEP 6: Stop Recording & Cleanup

**6.1 Stop ffmpeg Recording (Host Terminal)**
```bash
# Press Ctrl+C in the ffmpeg terminal
# Expected output:
frame= 2850 fps= 30 q=-1.0 Lsize=   12345kB time=00:01:35.00 bitrate=1064.2kbits/s speed=   1x
video:12340kB audio:0kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 0.040000%
```

**6.2 Verify Video File**
```bash
ls -lh bihar_maiden_voyage_*.mp4
# Expected: File size ~10-20 MB for 95-second mission

# Play video (optional)
vlc bihar_maiden_voyage_*.mp4
```

**6.3 Stop Docker Container**
```bash
docker stop hexacopter_gui
# Container auto-removes due to --rm flag
```

---

## 💾 STEP 7: Final Git Commit (The "Golden" Version)

**Purpose:** Lock in thesis-validated state with conventional commit

**7.1 Add All Files**
```bash
cd ~/thermal_hexacopter_project
git add .
```

**7.2 Commit with CEO Standard Message**
```bash
git commit -m "feat: complete maiden voyage in Bihar world and validate end-to-end AI survey

- Executed Level 3 survey mission in bihar_maize_farm world
- Validated simultaneous thermal monitoring and autonomous navigation
- Recorded 1920x1080 HD video of complete mission
- Confirmed 100% waypoint completion and disease detection alerts
- Final validation: 91.9% F1-score, 80.2% cost reduction
- Status: THESIS VALIDATED"
```

**Expected Output:**
```
[main abc1234] feat: complete maiden voyage in Bihar world and validate end-to-end AI survey
 X files changed, Y insertions(+), Z deletions(-)
 create mode 100644 bihar_maiden_voyage_20260215_004000.mp4
```

**7.3 Create Golden Tag**
```bash
git tag -a v4.0-thesis-validated -m "Final Validated PhD Project State: Maiden Voyage Complete"
```

**7.4 Verify Git History**
```bash
git log --oneline --graph --all
git tag -l
```

**Expected Tags:**
```
v3.0-defense-ready
v4.0-thesis-validated
```

---

## 🔍 Troubleshooting Guide

### Problem 1: "Cannot connect to X server"

**Symptom:** Docker fails with `Error: Can't open display: :0`

**Solution:**
```bash
# Enable X11 forwarding
xhost +local:docker

# Verify DISPLAY variable
echo $DISPLAY
# Should show: :0 or :1

# If empty, set it
export DISPLAY=:0
```

---

### Problem 2: "Gazebo GUI is black screen"

**Symptom:** Gazebo window opens but shows only black

**Solution:** Already included in launch command
```bash
-e LIBGL_ALWAYS_SOFTWARE=1
-e QT_X11_NO_MITSHM=1
```

If still black, try:
```bash
# Check OpenGL
glxinfo | grep "OpenGL version"

# Use VNC as alternative
vncserver :1
vncviewer localhost:1
```

---

### Problem 3: "thermal_monitor not found"

**Symptom:** `ros2 run agri_hexacopter thermal_monitor` fails

**Solution:**
```bash
# Rebuild workspace
docker exec hexacopter_gui /bin/bash -c \
    "cd /root/workspace && \
     source /opt/ros/humble/setup.bash && \
     colcon build --packages-select agri_hexacopter && \
     source install/setup.bash"
```

---

### Problem 4: "No thermal alerts during mission"

**Symptom:** Mission completes but no disease detections

**Debugging:**
```bash
# Check thermal camera topic
docker exec hexacopter_gui /bin/bash -c \
    "source /opt/ros/humble/setup.bash && \
     source /root/workspace/install/setup.bash && \
     ros2 topic hz /agri/thermal/image_raw"

# Expected: ~10 Hz
# If 0 Hz, thermal sensor plugin not loaded

# Verify thermal monitor subscriptions
docker exec hexacopter_gui /bin/bash -c \
    "source /opt/ros/humble/setup.bash && \
     source /root/workspace/install/setup.bash && \
     ros2 node info /thermal_monitor"
```

---

### Problem 5: "Mission doesn't start"

**Symptom:** level3_survey runs but drone doesn't arm

**Solution:**
```bash
# Check PX4 mode
docker exec hexacopter_gui /bin/bash -c \
    "source /opt/ros/humble/setup.bash && \
     source /root/workspace/install/setup.bash && \
     ros2 topic echo /fmu/out/vehicle_status --field nav_state"

# Wait 10-15 seconds after Gazebo opens for PX4 to boot
# Ensure MicroXRCEAgent is running (check terminal output)
```

---

## 📈 Success Metrics Checklist

After mission completion, verify:

- [ ] **Flight Stability:** Altitude error <±0.1m (target: ±0.06m)
- [ ] **Mission Completion:** 7/7 waypoints reached
- [ ] **AI Performance:** At least 1 disease alert generated
- [ ] **Video Quality:** 1920x1080 resolution, smooth 30 fps
- [ ] **Git Status:** v4.0-thesis-validated tag created
- [ ] **File Size:** Video ~10-20 MB (95 seconds × ~1 Mbps)

---

## 🎓 Supervisor Presentation Script

When demonstrating the video:

> "This recording shows the complete autonomous mission in our Bihar digital twin. The hexacopter executes a zig-zag survey pattern covering 80 square meters at 5-meter altitude. You can see the thermal AI system detecting disease hotspots in real-time, publishing GPS-tagged alerts. The mission achieves 100% waypoint completion with ±0.06-meter altitude stability, validating our Digital Twin Framework for risk-free algorithm development."

**Key Timestamps to Highlight:**
- 0:05 - Takeoff (show stable altitude hold)
- 0:15 - First waypoint transition (smooth navigation)
- 0:30 - Thermal alert in terminal (AI detection)
- 0:50 - Return-to-home initiated
- 1:35 - Safe landing on pad

---

## 🚀 Quick Command Summary

**One-Line Mission Execution (Advanced Users):**

```bash
# Terminal 1: Recording
ffmpeg -video_size 1920x1080 -framerate 30 -f x11grab -i :0.0 -c:v libx264 -preset ultrafast -crf 18 bihar_maiden_voyage_$(date +%Y%m%d_%H%M%S).mp4 &

# Terminal 2: Launch (wait for Gazebo to open)
cd ~/thermal_hexacopter_project && xhost +local:docker && docker run -it --rm --privileged --network=host -e DISPLAY=$DISPLAY -e LIBGL_ALWAYS_SOFTWARE=1 -e QT_X11_NO_MITSHM=1 -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd)/workspace:/root/workspace -v $(pwd)/scripts:/root/scripts --name hexacopter_gui hexacopter_lab_safe_copy -c "cd /root/workspace && chmod +x ../scripts/visual_hexacopter_bihar.sh && ../scripts/visual_hexacopter_bihar.sh"

# Terminal 3: Thermal AI (wait 15 seconds after Gazebo opens)
docker exec hexacopter_gui /bin/bash -c "source /opt/ros/humble/setup.bash && source /root/workspace/install/setup.bash && ros2 run agri_hexacopter thermal_monitor" &

# Terminal 4: Survey Mission (wait 5 seconds after thermal monitor)
docker exec hexacopter_gui /bin/bash -c "source /opt/ros/humble/setup.bash && source /root/workspace/install/setup.bash && /root/workspace/install/agri_bot_missions/bin/level3_survey"

# After landing: Stop recording (Ctrl+C in Terminal 1)
# Commit: git add . && git commit -m "feat: complete maiden voyage" && git tag -a v4.0-thesis-validated -m "Thesis validated"
```

---

## 📁 Output Files Checklist

After successful mission:

- [ ] `bihar_maiden_voyage_YYYYMMDD_HHMMSS.mp4` (video recording)
- [ ] Git commit with message starting with `feat: complete maiden voyage`
- [ ] Git tag `v4.0-thesis-validated`
- [ ] Terminal logs (optional: save with `script` command)

---

**Status:** ✅ **COMMAND CHEATSHEET COMPLETE**  
**Last Updated:** February 15, 2026  
**Version:** 1.0 (Maiden Voyage Edition)

**Abhishek, you are cleared for takeoff! 🚁🌾**
