# Indra-Eye Integration Guide for Existing Hexacopter Workspace

## 📋 Integration Steps

Based on your existing hexacopter workspaces, here's how to integrate Indra-Eye:

### Step 1: Identify Your Active Workspace

You have these hexacopter workspaces:
- `/home/abhishek/thermal_hexacopter_project/`
- `/home/abhishek/agri_hexacopter_ws/`
- `/home/abhishek/hexacopter-env/`

### Step 2: Copy Indra-Eye Source to Your Workspace

```bash
# Example: Using thermal_hexacopter_project
cd /home/abhishek/thermal_hexacopter_project

# Copy Indra-Eye packages to src/
cp -r /home/abhishek/Downloads/indra_eye_project/src/indra_eye_core src/
cp -r /home/abhishek/Downloads/indra_eye_project/src/indra_eye_supervisor src/
cp -r /home/abhishek/Downloads/indra_eye_project/src/indra_eye_sim src/

# Copy configuration files
mkdir -p config
cp -r /home/abhishek/Downloads/indra_eye_project/config/* config/

# Copy launch scripts
cp /home/abhishek/Downloads/indra_eye_project/launch_multi_terminal.sh .
cp /home/abhishek/Downloads/indra_eye_project/launch_tmux.sh .
cp /home/abhishek/Downloads/indra_eye_project/fly.py .
```

### Step 3: Build the Workspace

```bash
# Source ROS 2 (adjust path if needed)
source /opt/ros/humble/setup.bash

# Build
colcon build --symlink-install

# Source workspace
source install/setup.bash
```

### Step 4: Launch Indra-Eye

```bash
# Multi-terminal launch
bash launch_multi_terminal.sh

# Or Python launcher
python3 fly.py --mode sitl --qgc
```

## 🔧 Path Updates Needed

After copying, you may need to update paths in:
- `launch_multi_terminal.sh` - Change PROJECT_DIR
- `launch_tmux.sh` - Change PROJECT_DIR  
- `fly.py` - Change self.project_dir

## 📝 Quick Commands

```bash
# Copy everything to thermal_hexacopter_project
DEST=/home/abhishek/thermal_hexacopter_project
SRC=/home/abhishek/Downloads/indra_eye_project

cp -r $SRC/src/indra_eye_* $DEST/src/
cp -r $SRC/config $DEST/
cp $SRC/launch_*.sh $SRC/fly.py $DEST/
```

---

**Which workspace would you like to use?**
1. thermal_hexacopter_project
2. agri_hexacopter_ws
3. hexacopter-env
