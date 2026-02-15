# Indra-Eye Project Structure

## PhD-Standard Organization

```
indra_eye_project/
├── README.md                          # Quick reference
├── INDRA_EYE_MANUAL.md               # Complete operator's manual (10,000+ words)
├── CHEATSHEET.md                     # Command reference
├── fly.py                            # Master Python launcher ⭐
├── setup_and_run.sh                  # Installation script
├── run_mission.sh                    # Mission launcher (bash)
├── kill_and_fly.sh                   # Clean restart
├── docker-compose.hitl.yaml          # HITL Docker configuration
│
├── config/                           # All configuration files
│   ├── dds_bridge.yaml              # ROS 2 ↔ PX4 topic mapping
│   ├── px4_params_indra_eye.txt     # PX4 parameters
│   ├── hardware_map.yaml            # Jetson Orin Nano hardware config
│   ├── livox_config.json            # Livox LiDAR settings
│   └── qgc_custom_layout.json       # QGroundControl dashboard
│
├── docs/                             # Academic documentation
│   ├── lit_review.md                # 3,000-word literature review
│   ├── funding_ppt.md               # 12-slide funding proposal (₹9.13L)
│   └── thesis/                      # PhD thesis (LaTeX)
│       ├── main.tex
│       ├── chapters/
│       └── figures/
│
├── scripts/                          # Utility scripts
│   ├── validate_system.py           # System health check
│   ├── plot_trajectories.py         # PhD thesis plots
│   ├── calculate_rmse.py            # Performance metrics
│   └── generate_stats_table.py      # LaTeX table generation
│
├── src/                              # ROS 2 packages
│   ├── indra_eye_core/              # ES-EKF + MAVROS bridge
│   │   ├── include/indra_eye_core/
│   │   │   └── ekf_math.hpp         # Mathematical foundations
│   │   ├── src/
│   │   │   ├── es_ekf_node.cpp      # ES-EKF implementation
│   │   │   ├── mavros_bridge_node.cpp
│   │   │   └── path_aggregator_node.cpp
│   │   ├── package.xml
│   │   └── CMakeLists.txt
│   │
│   ├── indra_eye_supervisor/        # Anti-jamming supervisor
│   │   ├── src/
│   │   │   └── supervisor_node.cpp  # Spoofing detection
│   │   ├── package.xml
│   │   └── CMakeLists.txt
│   │
│   └── indra_eye_sim/               # Gazebo simulation
│       ├── launch/
│       │   ├── sitl_launch.py       # SITL launch file
│       │   └── hitl_launch.py       # HITL launch file
│       ├── worlds/
│       │   └── himalayan_terrain.world
│       ├── rviz/
│       │   └── indra_eye_mission.rviz
│       ├── models/                  # Gazebo models
│       ├── package.xml
│       └── CMakeLists.txt
│
└── logs/                             # Mission data
    ├── rosbags/                     # ROS bag recordings
    ├── screenshots/                 # RViz screenshots
    └── flight_logs/                 # PX4 logs
```

## File Count Summary

- **C++ Source Files**: 4 nodes (ES-EKF, Supervisor, MAVROS Bridge, Path Aggregator)
- **Header Files**: 1 (ekf_math.hpp)
- **Python Scripts**: 5 (fly.py, validate_system.py, plot_trajectories.py, etc.)
- **Launch Files**: 2 (SITL, HITL)
- **Configuration Files**: 5 (DDS, PX4, hardware, Livox, QGC)
- **Documentation**: 4 (README, Manual, Lit Review, Funding Proposal)
- **Build Files**: 6 (package.xml × 3, CMakeLists.txt × 3)

**Total**: 27+ core files

## Key Directories

### `/config` - Configuration Hub
All system configuration in one place:
- DDS bridge for PX4 communication
- PX4 parameters for ES-EKF integration
- Hardware mapping for HITL deployment
- Sensor-specific configs (Livox, QGC)

### `/docs` - Academic Documentation
PhD-level documentation:
- Literature review (3,000 words, 12 citations)
- Funding proposal (₹9.13L budget breakdown)
- Thesis chapters (LaTeX source)

### `/scripts` - Utility Tools
Analysis and validation:
- System validation before launch
- Trajectory plotting for thesis
- RMSE calculation vs. ground truth
- Statistics table generation

### `/src` - ROS 2 Packages
Three packages following ROS 2 conventions:
- `indra_eye_core`: Core navigation (ES-EKF, MAVROS, paths)
- `indra_eye_supervisor`: Anti-jamming logic
- `indra_eye_sim`: Simulation environment

### `/logs` - Mission Data
Organized data storage:
- ROS bags for replay and analysis
- Screenshots for thesis figures
- PX4 flight logs for debugging

## PhD Workflow Integration

### Data Collection
```bash
python3 fly.py --mode sitl --duration 1200 --record
```

### Analysis
```bash
python3 scripts/plot_trajectories.py --bag logs/rosbags/mission.bag
python3 scripts/calculate_rmse.py --bag logs/rosbags/mission.bag
```

### Thesis Integration
```bash
cd docs/thesis
# Figures auto-copied to figures/
pdflatex main.tex
```

## Version Control (.gitignore)

```
build/
install/
log/
logs/rosbags/*.bag
*.pyc
__pycache__/
.vscode/
*.swp
```

---

**🇮🇳 Jai Hind! 🇮🇳**
