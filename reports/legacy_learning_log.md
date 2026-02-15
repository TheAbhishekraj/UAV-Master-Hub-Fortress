### 📔 STEP 3: The `learning_log.md` (The Captain's Diary)
This is **vital**. Every time we fix an error (like the Gradle one), we write it here. This file will basically write your Thesis "Methodology" chapter for you!

**Copy and paste this into `learning_log.md`:**

```markdown
# 📔 PhD Research Learning Log
**"The Captain's Diary"**

## 📅 Session 1: Building the Foundation (Date: [Current Date])
**Goal:** Setup Docker Environment with PX4 v1.14 and ROS2 Humble.

### 🛑 Challenges Faced (The Monsters)
1.  **Gradle Error:** Tried to use PX4 v1.13, but Gradle 7.2 failed with "Could not find method compile()".
    * *Reason:* Incompatibility between old Gradle syntax and new Java versions on Ubuntu 22.04.
2.  **Fast-DDS Complexity:** The old MicroRTPS bridge required too many manual dependencies (Java, Fast-DDS-Gen).

### ✅ Solutions (The Weapons)
1.  **Upgraded to PX4 v1.14:** Switched to the modern stable release.
2.  **Removed Java:** PX4 v1.14 uses **Micro XRCE-DDS**, which doesn't need Java or Gradle.
3.  **Docker Shortcuts:** Created aliases (`launch_simulation`, `start_bridge`) to simplify commands.

### 🧠 Key Learnings
* **Micro XRCE-DDS** is the new standard for ROS2-PX4 communication. It is a client-agent architecture.
* **Docker Volumes** allow us to code on the host machine while running the code inside the container.

---
*(This file will be updated after every major milestone)*
🗺️ STEP 4: The roadmap.md (The Plan)
We will check these off as we go. It feels very satisfying!

Copy and paste this into roadmap.md:

Markdown

# 🛣️ PhD Research Roadmap

## 🟢 Phase 1: The Foundation (Current)
- [x] Design Dockerfile (Ubuntu 22.04 + ROS2 Humble)
- [ ] Build Docker Image (Running now...)
- [ ] Verify Connection (`verify_connection.py` script)

## 🟡 Phase 2: The "Frankenstein" Drone
- [ ] Modify SDF: Add Thermal Camera Link
- [ ] Modify SDF: Adjust weight/inertia for Payload
- [ ] Test Flight in Gazebo
## 📅 Entry 1: System Architecture Decision (Migration to PX4 v1.14)
**Date:** February 7, 2026
**Phase:** Environment Setup

### 🚩 The Technical Challenge
Initially, the project attempted to utilize **PX4 v1.13** with the **MicroRTPS Bridge**. However, during the Docker build process on **Ubuntu 22.04 (Jammy Jellyfish)**, a critical compatibility issue emerged:
* **Error:** `Could not find method compile() for arguments...` in Gradle.
* **Root Cause:** The legacy MicroRTPS bridge relies on **Java** and **Gradle** to generate code. PX4 v1.13 requires older Gradle versions (v6.x) that are difficult to maintain on modern Linux kernels, while newer Gradle versions (v7.0+) deprecated the commands required by the Fast-DDS generator.

### 💡 The Engineering Solution
I decided to migrate the system architecture to **PX4 v1.14 (Stable)**.
* **New Middleware:** Replaced MicroRTPS with **Micro XRCE-DDS**.
* **Benefit 1 (Stability):** This architecture removes the dependency on Java and Gradle entirely, eliminating the build failure.
* **Benefit 2 (Performance):** Micro XRCE-DDS offers a client-agent model that is more lightweight and efficient for the **Raspberry Pi 4** (Edge Device) compared to the older bridge.
* **Benefit 3 (Compatibility):** Native support for **ROS2 Humble**, ensuring smoother integration for the Thermal AI nodes later.

### 🛠️ Implementation Status
* **Dockerfile:** Updated to pull `PX4-Autopilot v1.14.0`.
* **Dependencies:** Removed OpenJDK and Gradle; added `Micro-XRCE-DDS-Agent`.
* **Outcome:** Build stability achieved; simulation environment now aligns with current industry standards.
## 🟠 Phase 3: The Bihar World
- [ ] Create `bihar_farm.world`
- [ ] Add crop textures and obstacles (trees, poles)

## 🔵 Phase 4: The Brain (AI)
- [ ] Integrate MobileNetV2 (TFLite)
- [ ] Create ROS2 Node for Thermal Detection
- [ ] "Red Box" Test: Detect heat source in simulation

## 🟣 Phase 5: The Mission
- [ ] Write Path Planning Algorithm (Lawnmower Pattern)
- [ ] End-to-End Simulation Test

## 📅 Entry 2: Professional ROS2 Restructuring
**Date:** [Current Date]
[cite_start]**Phase:** System Architecture [cite: 107]

### 🚩 The Requirement
To adhere to the "World-Class" engineering standard and the PhD Proposal Appendix, the project required a transition from a flat script directory to a scalable **ROS2 Package** structure.

### 🛠️ The Transformation
1.  [cite_start]**Created Package:** `agri_hexacopter`[cite: 109].
2.  **File Hierarchy:** Established standard folders (`launch`, `config`, `worlds`, `models`) to support future expansion into Simulation and AI.
3.  **Entry Points:** Configured `setup.py` and `package.xml` to allow the package to be built using `colcon build` and run using `ros2 run`.
4.  **Verification:** Migrated the connection test script to a modular format (`test_connection.py`).

### 🧠 Key Learnings
* **Setup.py vs Setup.cfg:** `setup.py` handles the installation logic, while `setup.cfg` ensures the Python scripts are executable and found by ROS2.
* **Colcon:** The build tool `colcon` processes the `package.xml` to understand dependencies and creates an `install/` directory, keeping the source clean.
