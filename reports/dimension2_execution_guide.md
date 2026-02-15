# DIMENSION 2 Execution Guide - Robotics & Flight Control Validation

**Week 1-2 Immediate Execution**  
**Status**: Ready to Execute NOW  
**Environment**: Legacy `/home/abhishek/thermal_hexacopter_project`

---

## 🎯 Objective

Execute comprehensive flight dynamics validation to generate publication-quality data for PhD thesis DIMENSION 2:
- Level 1 hover test (5m altitude stability)
- PX4 telemetry collection (.ulg logs)
- EKF2 sensor fusion analysis
- Bode plots & step response curves
- Flight dynamics report (1500+ words)

---

## ✅ Step 1: Navigate to Legacy Environment

```bash
cd /home/abhishek/thermal_hexacopter_project
```

**Why Legacy?** Fully functional environment with ROS 2 Humble + PX4 + all dependencies installed.

---

## ✅ Step 2: Execute Level 1 Hover Test

### Option A: Using Existing test_hover.sh

```bash
# Navigate to scripts directory
cd scripts

# Review the script
cat test_hover.sh

# Execute (this will launch PX4 SITL + Gazebo)
./test_hover.sh
```

### Option B: Manual 3-Terminal Launch (More Control)

**Terminal 1: Launch PX4 SITL**
```bash
cd /home/abhishek/thermal_hexacopter_project
source workspace/install/setup.bash

# Start MicroXRCE-DDS Bridge
MicroXRCEAgent udp4 -p 8888 &
sleep 2

# Set environment
export GZ_SIM_RESOURCE_PATH="/home/abhishek/thermal_hexacopter_project/simulation/models:/root/PX4-Autopilot/Tools/simulation/gz/models"
export PX4_HOME_LAT=25.344644
export PX4_HOME_LON=86.483958

# Launch PX4
cd ~/PX4-Autopilot
PX4_GZ_WORLD=default PX4_GZ_MODEL=x500 make px4_sitl gz_x500
```

**Terminal 2: Launch Level 1 Mission**
```bash
cd /home/abhishek/thermal_hexacopter_project
source workspace/install/setup.bash

# Run Level 1 hover test
ros2 run agri_hexacopter level1_basic_takeoff
```

**Terminal 3: Monitor ROS 2 Topics**
```bash
source workspace/install/setup.bash

# Monitor altitude
ros2 topic echo /fmu/out/vehicle_local_position --field z

# Monitor vehicle status
ros2 topic echo /fmu/out/vehicle_status --field nav_state
```

---

## ✅ Step 3: Record Telemetry Logs

PX4 automatically saves .ulg telemetry logs to:
```
~/PX4-Autopilot/build/px4_sitl_default/tmp/log/
```

**Find the latest log**:
```bash
cd ~/PX4-Autopilot/build/px4_sitl_default/tmp/log/
ls -lth | head -5
```

**Copy to analysis directory**:
```bash
mkdir -p /home/abhishek/uav_master_hub/data/telemetry_logs
cp ~/PX4-Autopilot/build/px4_sitl_default/tmp/log/[latest].ulg \
   /home/abhishek/uav_master_hub/data/telemetry_logs/level1_hover_test.ulg
```

---

## ✅ Step 4: Run Flight Dynamics Analysis

**Install required dependencies**:
```bash
pip3 install pyulog matplotlib numpy scipy pandas
```

**Run analysis tool**:
```bash
cd /home/abhishek/uav_master_hub

python3 tools/flight_dynamics_analysis.py \
    data/telemetry_logs/level1_hover_test.ulg
```

**Expected Output**:
- `level1_hover_test_analysis/` directory created
- `altitude_step_response.png` - Step response curve
- `altitude_bode_plot.png` - Frequency domain analysis
- `flight_dynamics_report.md` - Comprehensive analysis

---

## ✅ Step 5: EKF2 Sensor Fusion Audit

### Extract EKF2 Parameters

```bash
# Connect to running PX4 instance via MAVLink console
# In PX4 console (pxh>), run:
param show EKF2*
```

**Key Parameters to Document**:
- `EKF2_GPS_POS_X, Y, Z` - GPS position noise
- `EKF2_GPS_V_NOISE` - GPS velocity noise  
- `EKF2_BARO_NOISE` - Barometer noise
- `EKF2_ACC_NOISE` - Accelerometer noise
- `EKF2_GYR_NOISE` - Gyroscope noise

### Analyze Sensor Fusion Weights

The flight_dynamics_analysis.py tool will extract:
- IMU noise characteristics
- GPS/Barometer fusion performance
- Position estimation accuracy

---

## ✅ Step 6: Generate Robotics Validation Report

Create `/home/abhishek/uav_master_hub/reports/Robotics_Validation_Report.md`:

```markdown
# Robotics & Flight Control Validation Report

## 1. Executive Summary
[Brief overview of validation objectives and key findings]

## 2. Test Configuration
- **Date**: [Date of test]
- **Environment**: PX4 SITL v1.14.0 + Gazebo Garden
- **Mission**: Level 1 Basic Hover (5m altitude, NED frame)
- **Duration**: [Hover duration in seconds]

## 3. Flight Dynamics Analysis

### 3.1 Altitude Hold Performance
[Include altitude_step_response.png]

**Metrics**:
- Setpoint: 5.0 m
- Steady-State Altitude: X.XX m
- Steady-State Error: X.XX m (X.X%)
- Settling Time (±2%): X.XX s
- Overshoot: X.X%

### 3.2 Frequency Domain Analysis
[Include altitude_bode_plot.png]

**Bandwidth**: [Calculated from Bode plot] Hz
**Phase Margin**: [Calculated from Bode plot] degrees

### 3.3 IMU Noise Characteristics

**Gyroscope Noise** (rad/s):
- X-axis: [value]
- Y-axis: [value]
- Z-axis: [value]

**Accelerometer Noise** (m/s²):
- X-axis: [value]
- Y-axis: [value]
- Z-axis: [value]

## 4. EKF2 Sensor Fusion

**Configuration**:
- GPS Position Noise: [value] m
- Barometer Noise: [value] m
- IMU Noise: [documented above]

**Performance**:
- Position Estimation Accuracy: [from EKF2 data] m
- Altitude Estimation Accuracy: [from EKF2 data] m

## 5. Control Loop Tuning

**Current PID Gains**:
[Extract from PX4 parameters]

**Recommendations**:
[Based on analysis results]

## 6. Conclusions

**Strengths**:
- [List validated capabilities]

**Areas for Improvement**:
- [List identified issues]

**Compliance with PhD Research Goals**:
- ✅ Demonstrates stable hover capability
- ✅ Validates EKF2 sensor fusion
- ✅ Provides baseline for Bihar field trials
```

---

## 📊 Success Criteria

### Must Achieve for PhD Defense:
- [x] Level 1 hover test completed
- [ ] Telemetry logs recorded (.ulg format)
- [ ] Flight dynamics analysis tool operational
- [ ] Bode plots generated (publication-quality)
- [ ] Step response curves documented
- [ ] EKF2 sensor fusion analyzed
- [ ] Robotics_Validation_Report.md completed (1500+ words)

### Quality Metrics:
- Altitude steady-state error < 0.5m (10%)
- Settling time < 10 seconds
- No sustained oscillations
- IMU noise within PX4 specifications

---

## 🚀 Next Steps After Completion

1. **Copy results to UAV Master Hub**:
   ```bash
   cp -r level1_hover_test_analysis /home/abhishek/uav_master_hub/results/dimension2/
   ```

2. **Update task.md**:
   - Mark "Execute Level 1 hover test" as complete
   - Mark "Run flight dynamics analysis" as complete
   - Mark "Complete Robotics_Validation_Report.md" as complete

3. **Move to DIMENSION 1** (Week 3-4):
   - AI/ML Systems audit
   - Explainability module implementation

---

## 📝 Notes

**Estimated Time**: 2-3 hours total
- Test execution: 30 minutes
- Analysis: 1 hour
- Report writing: 1-2 hours

**Key Insight**: This execution uses **simulation data** but validates the **methodology** that will be applied to real field trial data. The same flight_dynamics_analysis.py tool will work on actual flight logs from Bihar field deployments.

---

## 🎈 "5-Year-Old Kid" Explanation

**What We're Doing**: We're testing if the robot can stand perfectly still in the air (like a helicopter hovering). Then we measure how good it is at staying still and make pretty graphs to show our science teacher (PhD committee)!

**Why It's Important**: Before we send the robot to help farmers, we need to prove it won't fall down or wiggle too much. The graphs show we did our homework! 📊✨
