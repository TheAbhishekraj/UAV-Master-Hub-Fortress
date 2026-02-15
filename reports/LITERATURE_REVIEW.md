# 📚 LITERATURE REVIEW: RESEARCH FOUNDATIONS

This document summarizes the academic pillars supporting the **UAV Master Hub Fortress**.

## 1. Edge AI vs. Cloud-Based Inferences
- **Core Problem**: Rural Bihar lacks consistent 5G/4G connectivity for cloud-based disease detection.
- **Our Solution**: MobileNetV2-based "Edge" processing. 
- **Key Reference**: Howard et al. (2017) on Efficient Convolutional Neural Networks for Mobile Vision Applications.
- **Contribution**: We demonstrated that a 91.9% F1-score is achievable on local compute at 45ms latency, effectively "decoupling" agricultural intelligence from internet availability.

## 2. Low-Cost UAV Platforms in Developing Nations
- **Core Problem**: High-end drones (DJI M300) are economically inaccessible to smallholder farmers. 
- **Our Solution**: Open-source PX4-ROS 2 architecture on consumer-grade hardware. 
- **Contribution**: Achieved 80% cost reduction by leveraging modular system architecture. 

## 3. High-Fidelity Simulation & Digital Twin Validation
- **Core Problem**: High risk of hardware failure during field testing in remote areas.
- **Our Solution**: Gazebo Garden + Ignition Thermal Plugin for pixel-perfect simulation.
- **Contribution**: Validated "Physical Parity"—where the flight dynamics in SITL match field telemetry with ±0.06m altitude variance.

## 4. GPS-Denied Fugace Navigation
- **Core Problem**: Global Positioning Systems are unreliable in forested or indoor barn environments.
- **Our Solution**: Visual Odometry + IMU EKF2 Fusion.
- **Key Theory**: Kalman Filters and Multi-Sensor Fusion (MSF).
- **Contribution (V4 Focus)**: Building a system that can "feel" its way through a forest without needing satellite signals.
