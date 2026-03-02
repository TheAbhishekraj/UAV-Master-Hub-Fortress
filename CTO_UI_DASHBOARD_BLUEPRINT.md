# 🎛️ CTO Blueprint: Unified Flight Readiness & Monitoring Dashboard

**Strategic Initiative:** Transitioning from fragmented diagnostic windows (Gazebo + QGroundControl + Terminal) to a single pane-of-glass UI for enterprise-grade autonomous operations.

---

## 🛑 Problem Statement: The Current UI Limitations

Based on the latest field simulations (Screenshots 1 & 2), we are facing severe monitoring fragmentation:
1. **QGroundControl Overload:** The screenshot demonstrates a critical `"Manual control lost"` and `"vehicle error"` warning in yellow, but lacks the granular underlying reasons (e.g., EKF rejection, visual odometry failure).
2. **Context Switching:** A pilot cannot simultaneously watch physical drone dynamics (Gazebo view) while monitoring the A* path planning footprint (red tracking lattice in QGC) and the raw ES-EKF diagnostics stream.
3. **Information Silos:** Critical metrics (thermal CPU load on Jetson, Visual Point Cloud count, `accel_noise_density` variance) are hidden in headless bash terminals.

---

## 🎯 The Goal: "Athena UI" (Unified Drone Command Center)

We must build a React/Next.js (or Qt/C++) dashboard that polls the ROS 2 DDS network directly, bypassing standard MAVLink wrappers. This dashboard must be split into **4 Quadrants**, heavily prioritizing *Flight Readiness* and *Mathematical Stability* over traditional pilot inputs.

---

### Quadrant 1: Absolute Stability & State Estimation (The "Inner Ear")
**Purpose:** Replace raw terminal outputs with visual health bars. If any metric dips below the safety threshold, Takeoff is strictly locked.

*   **Z-Variance Confidence:** Real-time gauge.
    *   *Green:* < 0.05m (Golden Hover)
    *   *Yellow:* 0.05m - 0.20m (Wind degradation)
    *   *Red:* > 0.20m (EKF Divergence - Auto RTL)
*   **Sensor Fusion Lock:** 
    *   [ ] GNSS (Satellites tracked, HDOP)
    *   [ ] VIO (Camera feature count, ideally > 50)
    *   [ ] LiDAR SLAM (Point cloud density)
*   **IMU Bias Trackers:** Live line charts showing Accelerometer and Gyroscope random walk against absolute temperature (Detects thermal drift before the drone crashes).

### Quadrant 2: Pre-Flight Readiness Checklist (Go/No-Go Array)
**Purpose:** Automate the manual inspection phase. A supervisor clicks "Arm", and the system independently verifies these nodes.

1.  **Hardware Handshake:** Battery Voltage check vs. payload draw curve. (Jetson Nano + Thermal Cam peaks 25W).
2.  **ROS 2 Node Discovery:** Are all 5 layers alive? (Explorer, Doctor, Sprayer, Path Planner, Master Commander).
3.  **Spoofing Immunity:** Current Mahalanobis Distance calculated between GNSS vs VIO. Must be `< 9.21`.
4.  **A* Path Allocation:** Validates that the uploaded zig-zag maize sweep does not intersect the hard-coded geofence.

### Quadrant 3: Spatial Intelligence & Path Execution (The Map)
**Purpose:** Clean up the QGroundControl spaghetti tracking map.

*   **Dull Map Rendering:** Desaturate the satellite imagery so the red/green pathing pops visually.
*   **Disease Heatmap Overlay:** As the drone flies, drop colored pins where the thermal camera spots "sick" plants, rendering a real-time agricultural vulnerability grid.
*   **GPS-Denial Perimeter:** If the drone is forced into VIO/SLAM mode, paint a translucent red bubble around the drone on the map indicating the growing 0.92% positional drift area.

### Quadrant 4: The Execution Pipeline (Mission Control)
**Purpose:** High-level tactical controls stripped of unnecessary manual joystick RC configurations.

*   **Master Progress Bar:** `% of defined acreage scanned.`
*   **The "Zeus" Button (Emergency Logic Override):** Instead of standard RTL, trigger a custom node that utilizes strict LiDAR mapping to retrace the exact 3D entry path backward, avoiding novel obstacles.
*   **Dynamic Re-routing:** A one-click `Regenerate Path` button if new vertical obstacles (e.g. tractors) appear in the field during the flight.

---

## 🚀 Development Roadmap for "Athena UI"

To bring your project to the next commercial level, here is how we build it:

1.  **Backend (The Bridge):** Deploy a `ros2-web-bridge` (using WebSockets) running inside the V5 Docker Golden Image to expose all `/indra_eye/diagnostics` and `/agri/mission/log` topics to localhost.
2.  **Frontend (The Glass):** Build a responsive **React (Next.js)** application. Use **Three.js** to render a live 3D clone of the drone's attitude, and **Mapbox GL** for the agricultural overlay.
3.  **Integration:** Package the web server natively into the `launch_fortress_demo.sh` script so the CTO dashboard opens automatically in a browser tab at "Lift Off".
