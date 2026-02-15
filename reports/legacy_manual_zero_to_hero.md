📘 PHD ROBOTICS HANDBOOK: ZERO TO HERO
Project: Autonomous Thermal-Imaging Hexacopter for Bihar Smallholder Farms Stack: ROS 2 Humble | PX4 v1.14 | Gazebo Classic | Docker Author: Abhishek

🏗️ PART 1: THE FOUNDATION (DOCKER)
1.1 The Concept: "The Lab in a Box"
In robotics, installing software directly on a laptop is dangerous. One wrong update can break the entire system. We use Docker to solve this.

The Image (The Blueprint): This is the "frozen" file we built (taking ~30 mins). It contains Ubuntu, ROS 2, and PX4. It is immutable (unchangeable).

The Container (The Room): When you run docker run, you create a temporary "room" based on the blueprint.

The Volume (-v): This is the Magic Portal. It connects a folder on your laptop to a folder inside the container.

Why crucial? It allows you to edit code on your laptop (safe) and run it inside Docker (fast) without rebuilding.

1.2 "Layer Caching"
Docker is built like a Lego tower.

Bottom Layers: OS, ROS 2, PX4 (Heavy, rarely change).

Top Layers: Your code (Light, changes often).

Optimization: We organized the Dockerfile so heavy stuff is at the top. If you change your code, Docker skips the heavy downloads and only updates the top layer in seconds.

📂 PART 2: THE ARCHITECTURE (FILE SYSTEM)
A professional ROS 2 workspace is organized by Function.

Plaintext

thermal_hexacopter_project/
└── workspace/              <-- THE "WS" (Run 'colcon build' here)
    ├── build/              <-- Temp files (Ignore these)
    ├── install/            <-- The "Cooked" binaries (System reads this)
    ├── models/             <-- THE BODY (Drone Hardware)
    │   └── agri_hexacopter_drone/
    │       ├── model.config      <-- ID Card
    │       └── model.sdf         <-- Physics Definition
    └── src/                <-- THE BRAIN (Source Code)
        └── agri_hexacopter/
            ├── package.xml       <-- Dependencies (The Contract)
            ├── setup.py          <-- The Installer (The Map)
            ├── launch/           <-- Start Scripts
            ├── config/           <-- Tuning Parameters
            ├── worlds/           <-- Simulation Environments
            └── agri_hexacopter/  <-- Python Logic Package
                ├── __init__.py   <-- The "Gatekeeper"
                └── mission.py    <-- The State Machine
🛠️ PART 3: THE BUILDER (COLCON)
3.1 What is colcon?
COLlective CONstruction. It is the ROS 2 build tool. Your project has Python scripts, C++ drivers, and XML models. The computer cannot read these directly.

Action: colcon build translates your "Raw Code" (src/) into "Executable Programs" (install/).

Location: MUST be run from the workspace/ folder.

3.2 The package.xml (The Contract)
This file tells Colcon what "ingredients" your code needs.

Example: <depend>rclpy</depend> tells Colcon: "Make sure the ROS Python library is present before building."

3.3 The setup.py (The Map)
This file tells Colcon where to put your files.

Entry Points: The most critical section.

Python

'console_scripts': [
    'mission_control = agri_hexacopter.mission_control:main',
],
Translation: "Create a command named mission_control. When run, execute the main function inside mission_control.py."

🧠 PART 4: THE BRAIN (PYTHON & ROS 2)
4.1 The __init__.py
Basic: An empty file.

Advanced: It transforms a regular folder into a Python Module. Without this, Colcon cannot "see" your python scripts, and the build will succeed but the code won't run.

4.2 Nodes & Topics
Node: A single worker (e.g., mission_control).

Topic: The "Pipe" they shout into.

Example: The Thermal Camera Node shouts data into /camera/thermal_image. The Mission Node listens to that topic.

🌍 PART 5: THE BODY (SIMULATION)
5.1 SDF (Simulation Description Format)
Gazebo uses SDF, not Python.

The World (bihar_maize.sdf): Defines the environment (Sun, Gravity, Ground, Crops).

The Model (model.sdf): Defines the Robot.

Links: Physical parts (e.g., pesticide_tank).

Joints: Connections (e.g., Tank is fixed to Frame).

Sensors: (e.g., thermal_camera plugin).

5.2 The Connection
We use a Launch File to spawn the model.sdf into the bihar_maize.sdf world.

🚀 PART 6: THE ORCHESTRATION (LAUNCH & CONFIG)
6.1 Launch Files (.launch.py)
This is the "Master Switch." Instead of typing 5 commands, you type one. It allows you to start multiple nodes (Brain + Camera + Bridge) simultaneously.

6.2 Parameters (.yaml)
Professional robotics separates Logic from Settings.

Code: fly_to(target_altitude)

YAML: target_altitude: 3.0

Benefit: You can change the altitude on the field without touching the code.

📝 PART 7: THE DAILY WORKFLOW (CHEAT SHEET)
This is your exact step-by-step process for every research session.

Step 1: Open the Lab
Bash

# Run on Host Laptop
docker run -it --privileged --network=host \
-v ~/thermal_hexacopter_project/workspace:/root/thermal_hexacopter/workspace \
thermal-hexacopter:v1.14
Step 2: Cook the Code (Inside Docker)
Do this every time you change a Python file.

Bash

cd workspace
colcon build --symlink-install
source install/setup.bash
Step 3: Launch the World
Bash

# Terminal 1
launch_simulation world:=bihar_maize_farm model:=agri_hexacopter_drone
Step 4: Launch the Brain
Bash

# Terminal 2
ros2 launch agri_hexacopter start_offboard.launch.py
Step 5: Debugging
"Is the camera working?" -> ros2 topic list

"What is the drone seeing?" -> ros2 run rqt_image_view rqt_image_view

"Why isn't it moving?" -> ros2 topic echo /agri/status_log
