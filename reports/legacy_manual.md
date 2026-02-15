Command: gedit manual.md Action: Delete everything in the file and paste this complete, all-in-one guide.

Markdown

# 📖 MASTER MANUAL: Agri-Hexacopter Research Lab
**PhD Project: Autonomous Thermal-Imaging Drone for Bihar Agriculture**

---

## 🏗️ PART 1: SYSTEM ACCESS (Docker)
**The Digital Lab**
You do not run code on your laptop directly. You run it inside the "Container."

### 1. Start the Lab
Run this command in a fresh terminal (Host Machine) to enter the drone environment:
```bash
xhost +local:docker
docker run -it --privileged \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --volume="$HOME/thermal_hexacopter_project/workspace:/root/thermal_hexacopter/workspace:rw" \
    --network=host \
    --name=hexacopter_lab \
    thermal-hexacopter:v1.14
Note: If the container is already running in another tab, enter it using: docker exec -it hexacopter_lab bash

⚙️ PART 2: DEVELOPMENT WORKFLOW
The Cycle: Code → Build → Run

1. Where to Write Code
Python Scripts: workspace/src/agri_hexacopter/agri_hexacopter/

Launch Files: workspace/src/agri_hexacopter/launch/

Maps (Worlds): workspace/src/agri_hexacopter/worlds/

2. How to Build (Compile)
Every time you change code, you must rebuild inside the container:

Bash

cd /root/thermal_hexacopter/workspace
colcon build
source install/setup.bash
🚁 PART 3: FLIGHT OPERATIONS (3-Terminal Protocol)
To run a mission, you need 3 separate terminals running inside the container.

📺 TERMINAL 1: The Simulation (World)
Goal: Starts Gazebo and spawns the drone.

Bash

launch_simulation
Visual Check: You should see the drone sitting on the grass.

🌉 TERMINAL 2: The Bridge (Communication)
Goal: Connects the Flight Controller (PX4) to ROS2.

Bash

start_bridge
Visual Check: Look for Agent listening on port 8888.

🧠 TERMINAL 3: The Brain (Your Code)
Goal: Runs your specific mission script.

Bash

# Always source before running!
source install/setup.bash

# Run the Connection Test
ros2 run agri_hexacopter test_connection
Visual Check: Output should say "✅ CONNECTION VERIFIED!"

🛠️ PART 4: DEBUGGING & TROUBLESHOOTING
Use this checklist if something crashes.

🛑 Issue: "Package 'agri_hexacopter' not found"
Cause: You didn't source the setup file after building.

Fix: Run source install/setup.bash in that terminal.

🛑 Issue: "Executable not found"
Cause: You added a script but didn't register it in setup.py.

Fix: Open workspace/src/agri_hexacopter/setup.py and add your script to the console_scripts list.

🛑 Issue: Gazebo is Black / Crashing
Cause: Graphics driver issue.

Fix: On your host machine (outside Docker), run xhost +local:docker again.

🛑 Issue: Bridge says "Client not connected"
Cause: The simulation (Terminal 1) isn't running or the drone crashed.

Fix: Restart launch_simulation in Terminal 1.

📂 PART 5: PROJECT REFERENCE
File Structure Map

Plaintext

workspace/src/agri_hexacopter/
├── config/             # PID gains & Battery params
├── launch/             # ROS2 Launch files
├── models/             # SDF Models (Drone & Camera)
├── worlds/             # Gazebo Maps (Bihar Farm)
├── agri_hexacopter/    # Python Source Code
│   ├── __init__.py
│   └── test_connection.py
├── package.xml         # Dependencies
└── setup.py            # Installation Logic

---

### 🚀 What's Next? (Moving to Phase 4)
Now that your manual is ready and your project structure is built:

1.  **Immediate Step:** Use **Part 3** of this manual to launch the simulation and verify the green tick one last time.
2.  **Next Major Task:** We will begin **Phase 4 (AI Integration)**. We need to place your MobileNet model into the `models` folder and write a script to read it.

**Is the Green Tick appearing in Terminal 3?**
