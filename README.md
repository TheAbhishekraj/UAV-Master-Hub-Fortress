# 🏛️ UAV-Master-Hub-Fortress
**A Professional Research Ecosystem for Autonomous Thermal-Imaging UAVs**

[![PhD Defense](https://img.shields.io/badge/PhD-KIIT%20University-gold)](https://kiit.ac.in)
[![Phase 1](https://img.shields.io/badge/Phase%201-SITL%20Maturity-brightgreen)](reports/SUCCESS_PHASE_2)
[![Phase 2](https://img.shields.io/badge/Phase%202-SITL%20Maturity-brightgreen)](reports/INDRA_EYE_EKF_VERIFIED.log)
[![Architecture](https://img.shields.io/badge/Architecture-Fortress%20v4.0-blue)]()
[![ROS2](https://img.shields.io/badge/ROS2-Humble--PX4-success)]()

---

## 👨‍🎓 Author & Supervision

| Field | Details |
|---|---|
| **Author** | Abhishek Raj (Roll No: 2581195) |
| **Email** | 2581195@kiit.ac.in |
| **Supervisor** | Prof. Pramod Kumar Mullick |
| **Institution** | KIIT University, Bhubaneswar |
| **Thesis Title** | *Resilient Autonomous UAV Systems for Precision Agriculture in GPS-Challenged Environments* |
| **Version** | Fortress v4.0 — SITL Maturity | March 2026 |

---

## 🏗️ The Fortress Architecture

A **Mono-Repo Research Hub** decoupling core infrastructure from mission-specific logic. Strict silo separation ensures reproducibility, immutability, and professional-grade data integrity.

### 🏛️ Repository Silos

| Silo | Purpose |
|---|---|
| `/shared_libs` | Global message definitions (`px4_msgs`, `agri_msgs`) and shared tools. |
| `/projects/thermal_hexacopter` | **Phase 1**: Autonomous Thermal-Imaging mission (AI Doctor). |
| `/projects/indra_eye` | **Phase 2**: GPS-Denied Navigation using SO(3) Error-State EKF. |
| `/assets` | Digital Twins: Gazebo worlds (`bihar_maize.sdf`) and UAV models. |
| `/reports` | Sealed Academic Evidence, System Audits, and Defense materials. |
| `/docker` | Immutable reproducible environment (Golden Image v4.0). |
| `/SUBMISSION_PACKAGE_MARCH_2026` | Final Dissertation Package with manifest checksums. |

---

## 📊 PhD Validated Metrics (SITL)

| Metric | Phase 1 (Thermal) | Phase 2 (Indra-Eye) | Status |
|---|---|---|---|
| **AI F1-Score** | 92.0% (MobileNetV2) | — | ✅ Validated |
| **ES-EKF Z-Variance** | — | **0.031m** (< 0.05m target) | ✅ Proven |
| **A* Search Path** | 44 cells (Euclidean bias) | — | ✅ Validated |
| **GPS Denial Recovery** | — | **100%** (SLAM\_MODE active) | ✅ Proven |
| **Farmer ROI** | **₹10,200/ha savings** | — | ✅ Certified |

---

## 🚀 Golden Demo Run (Supervisor Hardened)

The demo is optimized for stability using a **Split-Launch Protocol** to prevent bridge timeouts.

### 1. Emergency Restoration
If the simulation is not visible, run the one-click recovery script:
```bash
bash projects/indra_eye/restore_demo.sh
```

### 2. Manual Verification
- **Gazebo**: Check the landing pad for the `agri_hexacopter_drone`.
- **QGroundControl**: Confirm "Ready for Takeoff" heartbeats.
- **Diagnostics**:
```bash
docker exec uav_hub_golden bash -c "source /root/startup.sh && ros2 topic echo /indra_eye/diagnostics"
```

### 3. GPS Denial Proof
```bash
docker exec uav_hub_golden bash -c "source /root/startup.sh && ros2 topic pub -1 /indra_eye/simulate_gps_denial std_msgs/msg/Bool '{data: true}'"
```

---

## 🛡️ Key Engineering SEAL
- **QoS Policy**: TRANSIENT_LOCAL for high-frequency IMU persistence.
- **Rotation Math**: Lie Group exponential map for gimbal-lock prevention.
- **Integrity**: `MANIFEST_CHECKSUM_FREEZE.txt` protects all submission evidence.

---

**Jai Hind! 🇮🇳**
