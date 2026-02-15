# 📖 WEEKEND LEARNING GUIDE: MULTI-SENSOR FUSION (MSF)

To prepare for **Phase V4: GPS-Denied Navigation**, here is your 30-minute superhero training guide.

## 🎥 Essential High-Impact Videos

### 1. The "Inner Ear" of the Drone (IMU)
- **Title**: [How an IMU Works - Accelerometers, Gyros, and Magnetometers](https://www.youtube.com/watch?v=eqZgxR6eRjo)
- **Why watch?**: Understand why the drone needs an "inner ear" to stay level even when it can't see or hear the stars (GPS).

### 2. The "Eyes" of the Drone (Visual Odometry)
- **Title**: [Visual Odometry Explained Simply](https://www.youtube.com/watch?v=XhI_J87A_Fw)
- **Why watch?**: Learn how the drone uses a camera to track pixels and calculate its position—just like how you walk in the dark by feeling the walls.

### 3. The "Brain" of the Drone (EKF - The Kalman Filter)
- **Title**: [The Kalman Filter - 5-Minute Technical Intuition](https://www.youtube.com/watch?v=CaCcOwJPytQ)
- **Why watch?**: This is the "secret sauce" inside the PX4 EKF2 module. It’s how the drone decides which sensor to trust when one is lying.

---

## 🛠️ Concepts specifically for V4 (GPS-Denied)
- **State Estimation**: The drone's mathematical guess of where it is.
- **Optical Flow vs VO**: Using downward cameras vs forward cameras to "see" motion.
- **Fusion Weighting**: Telling the drone: "It's raining outside, ignore the eyes and trust the inner ear more."

---

**Next Session Focus**: We will apply this math directly to the `indra_eye` project to achieve $Z_{variance} < 0.05m$.

*Enjoy your Munger Sunday!* 🏯
