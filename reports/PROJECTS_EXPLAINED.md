# 🏗️ THE PROJECTS SILO: THE DIMENSIONS OF INNOVATION

Abhishek, this is the "Brain Center" of our Fortress. Each folder inside `/projects` represents a different "Dimension" of what your drone can do.

---

## 📁 1. `indra_eye/` (The Explorer's Eye)
**What it is**: This is the GPS-Denied Navigation project.
- **5-Year-Old Explanation**: This is the part of the drone that lets it find its way even when the lights are off (no GPS). It uses a special "Camera Eye" to see how the ground is moving so it never gets lost.
- **PhD Detail**: Uses Visual Odometry and Multi-Sensor Fusion (MSF) to achieve centimeter-level precision without satellite signals.

## 📁 2. `thermal_hexacopter/` (The Plant Doctor)
**What it is**: This is the mission-specific logic for the Bihar Maize farms.
- **5-Year-Old Explanation**: This is where we keep the drone's "Doctor Kit." It has the map of the farm and the instructions on how to fly in a zig-zag pattern to check every single plant.
- **PhD Detail**: Contains the ROS 2 mission nodes and launch files that orchestrate the autonomous 7-waypoint survey.

## 📁 3. `ai_models/` (The Thinking Brain)
**What it is**: This is the folder where the "Learning" happens.
- **5-Year-Old Explanation**: This is the drone's "Library." It contains the pictures and the rules it uses to know the difference between a healthy green plant and a sick hot plant.
- **PhD Detail**: Houses the MobileNetV2 architecture and the clustering algorithms that provide the 91.9% F1-score for disease detection.

---

## 🤝 How they work together:
1. **`indra_eye`** tells the drone **HOW** to move safely.
2. **`thermal_hexacopter`** tells the drone **WHERE** to go (the map).
3. **`ai_models`** tells the drone **WHAT** it is seeing.

They are all separate folders so that if you want to teach the drone to do something new (like V5: Swarming), you can just add a new folder without breaking the old ones!
