# Indra-Eye - Integrated Setup

## 📁 New Location

Indra-Eye has been moved to:
**`/home/abhishek/thermal_hexacopter_project/indra_eye_project/`**

## 🚀 Quick Launch

```bash
cd /home/abhishek/thermal_hexacopter_project/indra_eye_project

# Build workspace
source /opt/ros/humble/setup.bash  # Or your ROS distro
colcon build --symlink-install
source install/setup.bash

# Launch multi-terminal
bash launch_multi_terminal.sh

# Or use Python launcher
python3 fly.py --mode sitl --qgc
```

## 📋 Complete Project Structure

```
thermal_hexacopter_project/
├── indra_eye_project/          ← NEW: Complete Indra-Eye system
│   ├── src/
│   │   ├── indra_eye_core/
│   │   ├── indra_eye_supervisor/
│   │   └── indra_eye_sim/
│   ├── config/
│   ├── docs/
│   ├── scripts/
│   ├── launch_multi_terminal.sh
│   ├── launch_tmux.sh
│   ├── fly.py
│   ├── INDRA_EYE_MANUAL.md
│   └── CHEATSHEET.md
├── ros2_ws/                    ← Your existing workspace
└── ... (other thermal hexacopter files)
```

## 🔧 Integration Options

### Option 1: Use Indra-Eye Standalone
Build and run Indra-Eye in its own directory (recommended for testing):
```bash
cd /home/abhishek/thermal_hexacopter_project/indra_eye_project
colcon build --symlink-install
bash launch_multi_terminal.sh
```

### Option 2: Merge with Existing ROS 2 Workspace
Copy Indra-Eye packages to your existing ros2_ws:
```bash
cp -r /home/abhishek/thermal_hexacopter_project/indra_eye_project/src/* \
      /home/abhishek/thermal_hexacopter_project/ros2_ws/src/

cd /home/abhishek/thermal_hexacopter_project/ros2_ws
colcon build --symlink-install
```

## 📚 Documentation

All documentation is in the `indra_eye_project` folder:
- **INDRA_EYE_MANUAL.md** - Complete 10,000-word manual
- **CHEATSHEET.md** - Command reference
- **MULTI_TERMINAL_GUIDE.md** - Launch system guide
- **PROJECT_STRUCTURE.md** - File organization

---

**🇮🇳 Ready to launch! 🇮🇳**
