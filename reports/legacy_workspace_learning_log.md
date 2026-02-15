# 📘 PhD Research Log: Thermal Hexacopter Project

## 🗓️ Entry: Physics Stress Test & Payload Integration
**Component:** Pesticide Tank (0.5kg) on x500_heavy frame.

### 1. Center of Gravity (CoG)
- **Finding:** `<pose>0 0 -0.1 0 0 0</pose>` (10cm below center).
- **Insight:** This lowers the CoG, increasing "pendulum stability" during hover.
- **Future Note:** Liquid sloshing effects may require adjustment later.

### 2. Mass & Thrust-to-Weight Ratio
- **Finding:** `<mass>0.5</mass>` (500g).
- **Impact:** This is ~25% of the standard x500 weight.
- **Risk:** Drone may feel "sluggish" on takeoff.
- **Mitigation:** If lift is insufficient, increase PX4 parameter `MPC_THR_HOVER` to ~0.6 (60%).

### 3. Inertia Tensor ($I_{xx}, I_{yy}, I_{zz}$)
- **Finding:** Values set to `0.001`.
- **Analysis:** These are "stiff" placeholder values.
- **Theoretical Target:** $I \approx m \cdot r^2 = 0.5 \cdot (0.1)^2 = 0.005$
- **Verdict:** Safe for Phase 1 simulation, though rotational resistance is lower than reality.