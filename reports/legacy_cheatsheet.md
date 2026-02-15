# 🛠️ Engineering Master Cheatsheet
**PhD Project: Autonomous Thermal Hexacopter**

---

## 📂 1. NAVIGATING THE COMPUTER (Linux Basics)
*How to move around your files without a mouse.*

| Command | Name | What it does | Example |
| :--- | :--- | :--- | :--- |
| **`pwd`** | Print Working Directory | "Where am I right now?" | `pwd` |
| **`ls`** | List | Show me the files in this folder. | `ls` |
| **`ls -a`** | List All | Show hidden files (like `.bashrc`). | `ls -a` |
| **`cd foldername`** | Change Directory | Go inside a specific folder. | `cd workspace` |
| **`cd ..`** | Go Back | Go up one folder level (backwards). | `cd ..` |
| **`cd ~`** | Go Home | Go to your main user folder instantly. | `cd ~` |
| **`clear`** | Clear Screen | Wipes the messy text from the terminal. | `clear` |
| **`history`** | History | Shows the last 1000 commands you typed. | `history` |

---

## 📝 2. MANAGING FILES (Creation & Destruction)
*How to build and destroy things.*

| Command | Name | What it does | Example |
| :--- | :--- | :--- | :--- |
| **`mkdir folder`** | Make Directory | Creates a new folder. | `mkdir new_maps` |
| **`mkdir -p a/b`** | Make Path | Creates a folder inside a folder instantly. | `mkdir -p src/config` |
| **`touch file`** | Touch | Creates an empty file. | `touch readme.md` |
| **`gedit file`** | Text Editor | Opens a graphical editor to write code. | `gedit setup.py` |
| **`cp file1 file2`** | Copy | Makes a duplicate of a file. | `cp map.world map_backup.world` |
| **`mv file newloc`** | Move | Moves a file (or renames it). | `mv script.py src/scripts/` |
| **`rm file`** | Remove | Deletes a file (Permanent!). | `rm bad_code.py` |
| **`rm -rf folder`** | Remove Force | Deletes a whole folder and everything inside. | `rm -rf old_project` |
| **`cat file`** | Concatenate | Prints the file text to the screen (quick read). | `cat package.xml` |

---

## 🐳 3. DOCKER COMMANDS (The Digital Lab)
*How to control the simulation container.*

| Command | What it does |
| :--- | :--- |
| **`xhost +local:docker`** | **Unlock Graphics.** (Run on Host) Allows Docker to open simulation windows. |
| **`docker build -t name .`** | **Build Lab.** Cooks the recipe (Dockerfile) into an image. |
| **`docker images`** | **Check Inventory.** Lists all the "Lab Images" you have built. |
| **`docker run ...`** | **Enter Lab.** Starts the container (See manual for full command). |
| **`docker ps`** | **Status Check.** Shows running containers. |
| **`docker ps -a`** | **Dead Status.** Shows containers that stopped/crashed. |
| **`docker exec -it ID bash`** | **Portal.** Opens a new terminal inside a running container. |
| **`docker stop ID`** | **Emergency Stop.** Forcefully shuts down a container. |
| **`docker rm ID`** | **Cleanup.** Deletes a stopped container to save space. |

---

## 🤖 4. ROS2 & ROBOTICS (The Brain)
*How to make the drone think and fly.*

| Command | What it does | Critical Note |
| :--- | :--- | :--- |
| **`colcon build`** | **Compile.** Turns Python scripts into robot packages. | Run in `~/workspace` root. |
| **`source install/setup.bash`** | **Refresh.** Loads the new code you just built. | Run in **EVERY** new terminal. |
| **`ros2 run pkg node`** | **Run Code.** Starts a specific script. | `ros2 run agri_hexacopter test_connection` |
| **`ros2 topic list`** | **Check Sensors.** Lists available data streams. | Checks if bridge is working. |
| **`ros2 topic echo /topic`** | **Read Data.** Prints live sensor data to screen. | `ros2 topic echo /fmu/out/vehicle_status` |
| **`ros2 node list`** | **Check Brains.** Lists all running scripts. | Checks if your code crashed. |

---

## ⌨️ 5. KEYBOARD SHORTCUTS (Ninja Moves)
*Save seconds, save hours.*

* **`Tab`**: Auto-completes a filename or command (Type `cd work` + `Tab` → `cd workspace`).
* **`Up Arrow`**: Scroll through previous commands (Don't retype the same long command!).
* **`Ctrl + C`**: **PANIC BUTTON.** Stops the currently running program immediately.
* **`Ctrl + Shift + T`**: Opens a new Terminal Tab.
* **`Ctrl + Shift + V`**: Paste text into the terminal (Standard Ctrl+V often doesn't work).

---

## 🚨 6. PHD "RULE OF THUMB"
1.  **Always Source:** If the terminal says "Command not found," type `source install/setup.bash`.
2.  **Always Build:** If you changed the Python code but the robot ignores it, type `colcon build`.
3.  **Three Terminals:** You always need 3 tabs open:
    * 1. Simulation (`launch_simulation`)
    * 2. Bridge (`start_bridge`)
    * 3. Your Code (`ros2 run...`)
    
    # Step 1: Go to the documentation folder
cd ~/thermal_hexacopter_project/docs

# Step 2: Create the new file
gedit cheatsheet.md
chmod +x workspace/src/agri_hexacopter/agri_hexacopter/mission_control.py
