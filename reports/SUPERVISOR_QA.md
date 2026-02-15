# ❓ SUPERVISOR Q&A: THE TOUGH QUESTIONS

Prepare your defense with these targeted answers to anticipated supervisor probes.

## 🏛️ Technical Questions
**Q: Why choose MobileNetV2 over more complex models like YOLOv8?**
- **A**: "Efficiency and power consumption. For a hexacopter running on 6S batteries, minimizing CPU/GPU load is critical to extending mission time. MobileNetV2 provided the sweet spot of 91.9% accuracy at only 45ms latency."

**Q: How do you handle EKF2 drift in GPS-denied environments (V4)?**
- **A**: "We implement a prioritized Fusion Mask. When GPS variance spikes, the system automatically weights Visual Odometry (VO) and the high-frequency IMU data higher, keeping the drone centered through Multi-Sensor Fusion."

## 🌾 Field & Social Questions
**Q: Can a farmer with zero technical knowledge really operate this?**
- **A**: "Yes. Through the 'Golden Vault' initiative, the interface is reduced to 'One-Button' launch scripts. The complexity is hidden inside the Fortress architecture."

**Q: Is the 80% cost reduction sustainable for long-term maintenance?**
- **A**: "Absolutely. By using standardized components (Hexacopter frames, open-source PX4), we avoid proprietary repair lock-in. A local technician can replace a motor for ₹2000, vs a ₹50,000 factory repair from DJI."

## 🔬 Research Validity
**Q: What is the scientific proof of your 'Digital Twin' accuracy?**
- **A**: "We performed 100+ flights in both SITL and Physical Field environments. The variance in altitude and lateral positioning between the two was less than 5%, proving our simulation is a statistically significant representative of reality."
