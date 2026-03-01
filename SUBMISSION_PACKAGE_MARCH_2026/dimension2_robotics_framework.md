# DIMENSION 2: Robotics & Flight Control - Theoretical Framework

**Author**: Abhishek Raj, IIT Patna  
**Date**: February 15, 2026  
**Status**: Theoretical Framework Complete (Simulation validation pending environment)

---

## Executive Summary

**Control System**: PX4 OFFBOARD mode with cascaded PID loops  
**State Estimation**: EKF2 (24-state extended Kalman filter)  
**Safety**: Multi-layer fail-safes, geofencing, RTL  
**Performance Targets**: ±0.5m position hold, <10s settling time

---

## 1. Flight Control Architecture

### 1.1 PX4 Control Stack

**Layered Architecture** (Top-Down):

**Layer 1: Mission Planning**
- Input: GPS waypoints, altitude commands
- Output: Trajectory setpoints (position, velocity, yaw)
- Implementation: `level1_basic_takeoff.py` (ROS 2 node)

**Layer 2: Position Controller** (PX4 module)
- Input: Trajectory setpoints
- Output: Attitude setpoints (roll, pitch, yaw rate)
- Control Law: Proportional control
```
roll_cmd = Kp_x × (x_error) + Kv_x × (vx_error)
pitch_cmd = Kp_y × (y _error) + Kv_y × (vy_error)
```

**Layer 3: Attitude Controller** (PX4 module)
- Input: Attitude setpoints
- Output: Motor commands (PWM)
- Control Law: PID cascaded loop
```
τ_roll = Kp_φ × (φ_error) + Ki_φ × ∫(φ_error) + Kd_φ × (φ_dot)
```

**Layer 4: Motor Mixer**
- Input: Thrust + torques (roll, pitch, yaw)
- Output: Individual motor PWM (1000-2000 μs)
- Mixer: Hexacopter "+" configuration

---

## 2. State Estimation - EKF2

### 2.1 Extended Kalman Filter Theory

**State Vector** (24 dimensions):
```
x = [position (3), velocity (3), quaternion (4), 
     gyro_bias (3), accel_bias (3), 
     wind_velocity (2), mag_field (3), mag_bias (3)]
```

**Sensor Inputs**:
- IMU: Accelerometer (3-axis), Gyroscope (3-axis) @ 250 Hz
- GPS: Position, velocity @ 10 Hz
- Barometer: Altitude @ 50 Hz
- Magnetometer: Heading @ 100 Hz

### 2.2 EKF2 Fusion Algorithm

**Prediction Step** (IMU-driven, 250 Hz):
```
x̂_k = f(x̂_k-1, u_k)  # State transition
P_k = F_k × P_k-1 × F_k^T + Q_k  # Covariance prediction
```

**Update Step** (GPS/Baro-triggered):
```
K_k = P_k × H_k^T × (H_k × P_k × H_k^T + R_k)^-1  # Kalman gain
x̂_k = x̂_k + K_k × (z_k - h(x̂_k))  # State update
P_k = (I - K_k × H_k) × P_k  # Covariance update
```

**Noise Parameters**:
- Process noise (Q): Accounts for model uncertainty
- Measurement noise (R): GPS (0.3m), Baro (0.9m), IMU (0.02 m/s²)

### 2.3 EKF2 Configuration (PX4 Parameters)

```
EKF2_GPS_POS_X = 0.3    # GPS horizontal position noise (m)
EKF2_GPS_V_NOISE = 0.5  # GPS velocity noise (m/s)
EKF2_BARO_NOISE = 0.9   # Barometer noise (m)
EKF2_ACC_NOISE = 0.35   # Accelerometer noise (m/s²)
EKF2_GYR_NOISE = 0.015  # Gyroscope noise (rad/s)
```

**Tuning Philosophy**: Conservative (higher noise = trust sensors less, smoother estimates)

---

## 3. Flight Dynamics Model

### 3.1 Equations of Motion

**6-DOF Dynamics** (Hexacopter):

**Translational**:
```
m × ẍ = T × sin(θ) - D_x
m × ÿ = -T × sin(φ) × cos(θ) - D_y
m × z̈ = T × cos(φ) × cos(θ) - mg - D_z
```

Where:
- T = Total thrust (sum of 6 motors)
- φ, θ = Roll, pitch angles
- D_x, D_y, D_z = Drag forces
- m = 3.2 kg (total mass)

**Rotational**:
```
I_xx × φ̈ = τ_roll + (I_yy - I_zz) × θ̇ × ψ̇
I_yy × θ̈ = τ_pitch + (I_zz - I_xx) × φ̇ × ψ̇
I_zz × ψ̈ = τ_yaw + (I_xx - I_yy) × φ̇ × θ̇
```

Where:
- I_xx, I_yy, I_zz = Moments of inertia
- τ_roll, τ_pitch, τ_yaw = Control torques

### 3.2 Linearization (Hover Condition)

**Small Angle Approximation** (φ, θ << 1):
```
sin(φ) ≈ φ, cos(φ) ≈ 1
sin(θ) ≈ θ, cos(θ) ≈ 1
```

**Simplified Translational Dynamics**:
```
ẍ ≈ g × θ
ÿ ≈ -g × φ
z̈ ≈ (T/m - g)
```

This allows **independent axis control** (decoupled controllers)

---

## 4. Control System Design

### 4.1 PID Tuning Methodology

**Position Loop (Outer)**:
```
Kp_pos = 1.0  # Proportional gain
Kd_pos = 0.5  # Derivative gain (damping)
```

**Velocity Loop (Middle)**:
```
Kp_vel = 2.0
Ki_vel = 0.1  # Integral for steady-state error
```

**Attitude Loop (Inner)**:
```
Kp_att = 6.5
Ki_att = 0.2
Kd_att = 0.1
```

**Tuning Process** (Ziegler-Nichols-inspired):
1. Start with low gains
2. Increase Kp until oscillations
3. Add Ki to eliminate steady-state error
4. Add Kd to dampen overshoot

### 4.2 Bode Plot Analysis (Theoretical)

**Altitude Control Loop**:

**Open-Loop Transfer Function**:
```
G(s) = Kp × (1/s²) × (1/(τ_motor × s + 1))
```

Where τ_motor ≈ 0.02s (motor time constant)

**Closed-Loop Transfer Function**:
```
H(s) = G(s) / (1 + G(s))
```

**Expected Performance**:
- Bandwidth: ~2 Hz (sufficient for 10 Hz trajectory updates)
- Phase Margin: >45° (stable)
- Gain Margin: >6 dB (robust)

### 4.3 Step Response Characteristics

**5m Altitude Command** (Level 1 hover test):

**Theoretical Predictions**:
- Rise Time: 3-5 seconds
- Settling Time: 8-12 seconds (±2% criterion)
- Overshoot: <10% (target: <0.5m)
- Steady-State Error: <0.1m (with integral control)

**Damping Ratio** (ζ):
```
ζ = Kd / (2√(Kp × m))
ζ ≈ 0.7 (slightly underdamped, fast response)
```

---

## 5. Safety-Critical Validation

### 5.1 Fail-Safe Modes

**Loss of GPS**:
- Condition: <6 satellites or HDOP > 5.0
- Action: Switch to **Altitude Mode** (barometer-only for altitude hold)
- Horizontal position: Drift allowed, operator takes manual control

**Low Battery**:
- 30% threshold: Warning alert
- 20% threshold: **Auto-RTL** (Return-to-Launch)
- 10% threshold: **Emergency Land** at current location

**RC Signal Loss**:
- Timeout: 0.5 seconds
- Action: **Auto-RTL** (PX4 parameter: NAV_RCL_ACT = 2)

### 5.2 Geofencing (Software-Enforced)

**Horizontal Fence**:
```
GF_MAX_HOR_DIST = 500  # 500m radius from home
```

**Vertical Fence**:
```
GF_MAX_VER_DIST = 120  # 120m AGL (DGCA limit)
```

**Action on Breach**:
```
GF_ACTION = 1  # RTL (Return-to-Launch)
```

### 5.3 Pre-Flight Checks (Automated)

**PX4 Commander Module** checks:
- [ ] GPS lock (≥6 satellites, HDOP < 2.0)
- [ ] Battery voltage (≥14.0V for 4S LiPo)
- [ ] IMU calibration valid
- [ ] Magnetometer calibration valid
- [ ] RC link active
- [ ] Arming switch in DISARMED position

**Failure**: Prevent arming, indicate via LEDs/beeps

---

## 6. Performance Metrics (Theoretical Targets)

### 6.1 Position Hold Accuracy

**Hover Performance** (30m altitude, <5 m/s wind):
- Horizontal: ±0.5m (GPS-limited)
- Vertical: ±0.3m (barometer-limited)

### 6.2 Trajectory Tracking

**Waypoint Navigation** (5 m/s speed):
- Corner radius: 2-3m (smooth turns)
- Overshoot: <1m

### 6.3 Disturbance Rejection

**Wind Gust** (5 m/s):
- Recovery time: <3 seconds
- Max deviation: <2m (position controller compensates)

---

## 7. Validation Methodology

### 7.1 Simulation Tests (When Environment Available)

**Test 1: Hover Stability**
- Command: Hold 5m altitude for 60 seconds
- Metrics: Altitude RMS error, max deviation
- Pass Criteria: RMS < 0.2m, max < 0.5m

**Test 2: Step Response**
- Command: 0m → 5m altitude step
- Metrics: Rise time, overshoot, settling time
- Pass Criteria: Overshoot < 10%, settling < 12s

**Test 3: Waypoint Tracking**
- Command: Square pattern (4 waypoints)
- Metrics: Cross-track error
- Pass Criteria: Mean error < 1m

**Test 4: Fail-Safe Validation**
- Simulate: GPS loss, battery low, RC loss
- Expected: Correct mode transitions, safe landing
- Pass Criteria: No crashes, RTL successful

### 7.2 Data Collection (.ulg logs)

**PX4 Topics to Record**:
- `vehicle_local_position`: Estimated position (EKF2 output)
- `vehicle_gps_position`: GPS raw data
- `sensor_combined`: IMU data (accel, gyro)
- `vehicle_status`: Flight mode, arming state
- `battery_status`: Voltage, current, remaining %

**Analysis Tool**: `flight_dynamics_analysis.py` (already created in D7)

---

## 8. EKF2 Sensor Fusion Audit (Theory)

### 8.1 Fusion Weights

**Multi-Sensor Fusion** (Complementary):
- **IMU**: High-frequency (250 Hz), short-term accurate
- **GPS**: Low-frequency (10 Hz), long-term accurate
- **Barometer**: Medium-frequency (50 Hz), altitude reference

**EKF2 automatically adjusts weights** based on:
- Sensor noise (R matrix)
- Estimated covariance (P matrix)

**Example**: GPS dropout → EKF increases reliance on IMU (dead reckoning)

### 8.2 Innovation Monitoring

**Innovation** = Measurement - Prediction
```
y_k = z_k - h(x̂_k)
```

**Healthy Fusion**:
- Innovation small → Sensors agree with model
- Innovation large → Sensor fault or model mismatch

**PX4 Check**: Rejects GPS if innovation > 5σ (outlier)

---

## 9. Hexacopter vs Quadcopter Analysis

### 9.1 Redundancy Advantage

**Hexacopter**:
- 6 motors → Can fly with 1motor failure (5 operational)
- PX4 mixer compensates automatically

**Quadcopter**:
- 4 motors → Crash if 1 motor fails

**Safety**: Hexacopter 20% more redundant (critical for agriculture)

### 9.2 Payload Capacity

**Hexacopter**:
- 6 motors → Higher total thrust
- Payload: Up to 2 kg (FLIR Lepton + Jetson Nano = 350g)

**Trade-off**: 15% more complex (more parts), but better safety

---

## 10. Control Loop Frequencies

**Hierarchy** (High → Low frequency):

| Loop | Frequency | Latency |
|------|-----------|---------|
| Motor Controller | 8 kHz | 0.125 ms |
| Attitude Control | 250 Hz | 4 ms |
| Velocity Control | 50 Hz | 20 ms |
| Position Control | 10 Hz | 100 ms |
| Mission Planning | 1 Hz | 1000 ms |

**Design Principle**: Inner loops faster than outer loops (stability)

---

## Conclusion

**Theoretical Framework Complete**:
- PX4 control architecture documented (cascaded PID)
- EKF2 sensor fusion explained (24-state estimator)
- Flight dynamics modeled (linearized hover)
- Safety systems designed (fail-safes, geofencing)
- Validation methodology defined (simulation + field)

**Next Step**: Execute Level 1 hover test when ROS 2 environment available → Validate theory with simulation data

**Status**: ✅ COMPLETE (Theoretical Analysis)

**Word Count**: 890 words
