# 🎮 Manual Demonstration Guide: QGroundControl Path Planning & Recording

This guide provides exactly how to perform a **Manual Interruption & Flight Plan Demonstration** for your PhD Committee while ensuring all flight data, visuals, and metrics are successfully captured as hard evidence.

---

## 📹 1. Video & Image Capture

To prove the simulation is running smoothly in real-time, you have two flawless methods for video recording:

### Method A: Gazebo Built-In Recorder (Best for 3D physics)
1. In the **Gazebo Simulator** window (the 3D world), look at the very top-right corner.
2. Click the small **Video Camera Icon** (📹) to start recording.
3. Your video will be saved as an `.mp4` file directly in your home directory or `~/.ignition/rendering/`.
4. To capture stunning screenshots of the Hexacopter hovering, press the **Camera Icon** (📷) right next to it.

### Method B: Ubuntu OS Screen Record (Best for entire dashboard)
To capture QGroundControl and the Gazebo simulator at the same time:
1. Simply press `Ctrl + Alt + Shift + R` on your keyboard.
2. A red dot will appear at the top-right of your Ubuntu screen, indicating recording has started. Press the hotkey again to stop.

---

## 📈 2. Automated ROS 2 Data Logging

You **do not need to do anything manually** to get your data logs!
The new `launch_fortress_demo.sh` dashboard automatically spins up a background `rosbag_recorder` node the second the simulation starts.

Every time you run the simulation, a fully timestamped archive containing:
* `/indra_eye/diagnostics` (ES-EKF Math)
* `/fmu/out/vehicle_gps_position`
* `/fmu/out/vehicle_local_position`

Is saved directly into 👉 `/tmp/fortress_evidence/golden_bag_YYYYMMDD_HHMMSS/`

---

## 🗺️ 3. QGroundControl Path Planning in Munger Farm

If Professor Mullick asks you to draw a custom flight path across the field to prove the AI responds dynamically, follow these steps:

1. **Open Plan View:** In QGroundControl, click the **Map Icon (Plan)** in the top-left corner.
2. **Create the Waypoints:**
   - Click on the screen to drop **Waypoints** above the green maize field.
   - *Pro-tip:* Keep the Altitude set to **10 meters** for a great view.
   - Alternatively, use the **Pattern -> Survey** tool to draw a grid over the entire farm instantly.
3. **Upload to Drone:** Once your path is drawn, look at the top-right corner of QGC and click **Upload Required**.
4. **Execute Mission:**
   - Switch back to the **Paper Airplane Icon (Fly View)**.
   - A slider will appear at the bottom: `"Slide to Confirm Mission Start"`.
   - Slide it! The Hexacopter will autonomously Takeoff -> Navigate to Waypoints -> Land.

---

## 🌩️ 4. The "Ultimate Flex" (Manual GPS Denial)

While the Hexacopter is actively flying your custom QGC path:
1. Bring up your **"Supervisor Override Panel"** terminal window.
2. Hit `[ENTER]` to instantly simulate a massive GPS drop.
3. Point out to your committee that the hexacopter **does not crash** or jitter—it smoothly transitions to the Indra-Eye $SO(3)$ ES-EKF SLAM mode and finishes the QGC mission blindly!
