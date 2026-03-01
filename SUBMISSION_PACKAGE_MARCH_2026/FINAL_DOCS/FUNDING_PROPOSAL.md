# Project Indra-Eye: Hardware Procurement & Funding Proposal 
**Phase 3 Transition: Moving from 'Digital Fields' to 'Real Munger Terrain'**

**Candidate:** Abhishek Raj (Roll No: 2581195)
**Supervisor:** Prof. Pramod Kumar Mullick

---

## 1. Executive Summary & The Requirement
The Fortress v4.0 Architecture has achieved 100% SITL maturity. The $SO(3)$ Error-State Kalman Filter (ES-EKF) math is fully verified. However, simulated time is infinite. To ensure the Indra-Eye logic triggers fast enough to avoid physical collision in the complex, humid riverine geography of Munger, Bihar, we must validate the *Computational Latency*.

To demonstrate this in the field, we require the **₹2,00,200 (20% Provision)** hardware grant.

![Architecture Context Placeholder](https://via.placeholder.com/800x400?text=Indra-Eye+Hardware+Integration+Architecture)

---

## 2. The Justification: Computational Latency vs. Dynamic Terrain

> *"Sir, in a controlled lab, a basic drone works. In the riverine terrain of Bihar, computational latency kills. This funding ensures our 'Inner Ear' math finishes computing before the drone hits a tree."*

To run dense $SO(3)$ manifold calculations and deep-learning visual inferences simultaneously, edge-computing hardware is not a luxury—it is the prerequisite for safety.

### 2.1 NVIDIA Jetson Orin Nano (Central Compute Node)
* **Estimated Cost:** ₹55,000
* **Mathematical Necessity:** Standard Pixhawk microcontrollers run at hundreds of Megahertz. The ES-EKF integrating 15-dimensional error vectors ($\delta \mathbf{x}$) alongside the MobileNetV2 processing requires parallel floating-point operations. The 40 TOPS provided by the Orin Nano guarantees a system-wide computational cycle under 100ms.

### 2.2 Livox Mid-360 LiDAR (Primary Localization Sensor)
* **Estimated Cost:** ₹85,000
* **Terrain Necessity:** The target environment suffers from severe visual noise—high humidity fogs RGB lenses, and intense sunlight creates blinding glare. Traditional stereo-camera VIO will fail catastrophically. The Livox Mid-360 non-repetitive scanning LiDAR is immune to ambient glare, ensuring the ES-EKF receives continuous, ground-truth odometry even when "the stars go dark."

### 2.3 Frame, Actuation, and Integration Components
* **Estimated Cost:** ₹60,200
* **Necessity:** High-torque motors, carbon-fiber frame, power-distribution boards, and the physical micro-sprayer payload mechanism to handle the added weight of the Orin and LiDAR modules.

---

## 3. Socioeconomic ROI
This ₹2,00,200 investment provisions the creation of a physical prototype that enables a **₹10,200/ha annual saving** for the local maize farmers of Bihar, cementing the University's commitment to frugal, high-impact societal engineering.

![Economic Flow Placeholder](https://via.placeholder.com/800x400?text=Socioeconomic+Flowchart+Munger)

**We respectfully submit this High Bid for urgent review and approval to commence Phase 3 Hardware-in-the-Loop (HITL) integration.**
