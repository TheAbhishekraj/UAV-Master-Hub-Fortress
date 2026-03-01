# HITL Funding Proposal — 5-Slide Presentation Outline
## "From Algorithm to Reality: Hardware-in-the-Loop Validation"
### Livox Mid-360 | Intel RealSense D435i | NVIDIA Jetson Orin

---

## Slide 1: The SITL Success (What We Proved)
**Title**: *"500 Virtual Missions — Algorithm Validated"*

### Key Results (SITL Phase)
- **ES-EKF Z-variance**: 0.031m (target: < 0.05m) ✅
- **GPS Denial Recovery**: 100% of 500 Monte Carlo runs ✅
- **VIO Fallback latency**: < 12ms (simulated) ✅
- **Thermal AI F1-Score**: 92% on 3,200-image dataset ✅

### The Remaining Question SITL Cannot Answer
> *"Does the ES-EKF maintain the 10ms control loop deadline on embedded ARM hardware, with real sensor noise, real airflow vibration, and real Bihar maize field conditions?"*

**SITL = Algorithm Proof | HITL = Latency Proof**

---

## Slide 2: The Reality Gap (Why SITL Is Not Enough)
**Title**: *"What Simulation Cannot Simulate"*

| Factor | SITL (Current) | HITL (Required) |
|---|---|---|
| IMU noise | Gaussian model | Real Bosch BMI088 noise |
| VIO latency | Instantaneous | 33ms RealSense pipeline + USB |
| LiDAR dropouts | None | Beam scatter in dense canopy |
| Vibration | None | Motor resonance at 4,800 RPM |
| Compute budget | Unlimited PC | 15W TDP on Jetson Orin |
| Temperature | 25°C constant | 5°C to 45°C Bihar field range |

**Conclusion:** A 12ms simulation latency could become a 45ms physical latency — violating the PX4 safety threshold.

---

## Slide 3: The Hardware Requirement
**Title**: *"₹6,32,000 — Premium HITL + High-Performance Simulation Stack"*

### Sensor Suite (HITL Hardware)

#### Primary LiDAR: Livox Mid-360 (₹95,000)
- 360° horizontal, 59° vertical FOV
- 200,000 points/second (10× Velodyne VLP-16)
- Non-repetitive scan pattern — **essential for canopy-dense ADZs**
- Native `livox_ros_driver2` → `ros2_livox` → ES-EKF SLAM update
- Power: 8W at 5V (fits X500 power budget)

#### Stereo Camera: Intel RealSense D435i (₹32,000)
- 848×480 stereo at 90fps, global shutter
- Built-in IMU (BMI055) — synchronized with depth at µs precision
- `realsense2_camera` ROS 2 Humble package — zero integration work
- Powers the `/camera/stereo/odom` → ES-EKF VIO update pipeline

#### Edge Compute: NVIDIA Jetson Orin NX 16GB (₹75,000)
- 100 TOPS AI performance — upgraded from Nano for real-time SLAM
- Runs: TFLite thermal inference (67ms) + ES-EKF (10ms loop) + ROS 2 simultaneously
- ARM Cortex-A78AE — representative of Tier-1 production deployment hardware

### Supporting Infrastructure
| Item | Cost |
|---|---|
| RF-Shielded Faraday Enclosure (GPS denial testing) | ₹28,000 |
| Cables, vibration mounts, high-vibration isolators | ₹18,000 |
| Contingency 15% (hardware) | ₹40,500 |
| **HITL Hardware Sub-total** | **₹2,88,500** |

### Future Simulation Expansion (Training + Scaling)
| Item | Cost |
|---|---|
| **ASUS ROG Strix SCAR 18 / Alienware m18 R2** (i9-14900HX, 64GB DDR5, 2TB NVMe, RTX 4080 16GB) | ₹2,00,000 |
| **NVIDIA RTX 4090 24GB** (PCIe-Desktop, CUDA training server for YOLOv8 + Gazebo offload) | ₹1,50,000 |
| SSD Storage Expansion (4TB NVMe) | ₹15,000 |
| UPS + Surge Protection | ₹8,500 |
| **Simulation Hardware Sub-total** | **₹3,73,500** |

---

## Slide 4: The HITL Test Protocol
**Title**: *"How We Will Prove Latency"*

### 3-Phase Test Plan

**Phase A — Benchtop (Week 1-2)**
- Mount Livox + RealSense on static rig
- Run ES-EKF at 100Hz, measure CPU utilization
- Criterion: < 60% CPU on Jetson Orin at nominal load

**Phase B — Indoor HITL (Week 3-4)**
- Mount full sensor stack on X500 frame (static, powered)
- Drive all sensors simultaneously with Gazebo bridge
- Criterion: End-to-end latency < 10ms per EKF cycle

**Phase C — Outdoor Field Validation (Week 5-8)**
- 2-ha Bihar maize test plot, Fapur Block, Patna
- 20 GPS-denial events (Faraday tent over GPS antenna)
- Criterion: Z-variance < 0.05m throughout denial period
- Criterion: Thermal AI detects minimum 90% of injected anomalies

---

## Slide 5: Return on Investment
**Title**: *"₹2L to Prove ₹10,200/Farmer/Year at Scale"*

### The Socioeconomic Case

**Current**: Algorithm proven in simulation. System cannot be commercially deployed without HITL certification.

**After HITL**: 
- DGCA type-approval pathway opens (requires hardware test evidence)
- Technology transfer license to Bihar AgriTech Cooperative feasible
- Target: 500 farmers × 2 ha × ₹10,200 savings = **₹1.02 Crore / year** aggregate impact

### Research Outputs from HITL Phase
1. **Journal Paper**: "Real-Time ES-EKF Performance on Embedded ARM for Agricultural UAV Navigation" → *IEEE RA-L*
2. **Conference**: ICRA 2027 hardware demonstration
3. **Patent Filing**: GPS-denied navigation with non-repetitive LiDAR SLAM

### The Funding Ask
> ₹2,00,200 — **20% of total grant** — unlocks the remaining 80% of the project's commercial potential.
> 
> *"This is not an expense. This is the keystone that converts a PhD algorithm into a product."*

---

## Budget Summary Table

| # | Item | Amount (₹) | Justification |
|---|---|---|---|
| 1 | Livox Mid-360 LiDAR | 95,000 | 360° non-repetitive scan for ADZ canopy |
| 2 | Intel RealSense D435i | 32,000 | Stereo VIO + built-in IMU for ES-EKF |
| 3 | NVIDIA Jetson Orin NX 16GB | 75,000 | 100 TOPS — Tier-1 production compute |
| 4 | Faraday GPS Denial Enclosure | 28,000 | Reproducible indoor GPS denial lab |
| 5 | Integration Hardware | 18,000 | Premium vibration isolators + cables |
| 6 | Contingency (15%) | 40,500 | Component failure + import duty buffer |
| 7 | **ASUS ROG Strix SCAR 18 / Alienware m18 R2** | 2,00,000 | i9-14900HX, 64GB DDR5, RTX 4080 — SITL + multi-agent training |
| 8 | **NVIDIA RTX 4090 24GB** (Desktop PCIe) | 1,50,000 | Full YOLOv8 fine-tuning + Gazebo multi-drone GPU render |
| 9 | SSD Storage + UPS | 23,500 | 4TB NVMe data logging + surge protection |
|   | **GRAND TOTAL** | **₹6,62,000** | **HITL + Premium Simulation Stack** |

### Funding Split
| Category | Amount | % of Ask |
|---|---|---|
| HITL Sensor Hardware | ₹2,88,500 | 43.6% |
| Simulation / Training Infra | ₹3,73,500 | 56.4% |
| **Total** | **₹6,62,000** | **100%** |

---

*Prepared by: Abhishek Raj (2581195@kiit.ac.in) | KIIT University, Bhubaneswar*
*Supervisor: Prof. Pramod Kumar Mullick*
*Funding Request Ref: KIIT/PhD/2026/UAV-HITL-001 | March 2026*
