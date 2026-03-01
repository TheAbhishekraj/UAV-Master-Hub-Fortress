#!/usr/bin/env python3
"""
full_autonomy.launch.py
=====================================================================
ROS 2 launch file for the 5-Layer Autonomous Agricultural UAV System.

Launches all nodes in dependency order:
  1. MSF Bridge (V4)         — sensor fusion online first
  2. Path Planner (V4)       — ready before mission starts
  3. Thermal Monitor (V2)    — analyse as soon as drone is up
  4. Sprayer Control (V3)    — ready to act on V2 detections
  5. Image Collector (V1)    — drives the survey flight
  6. Mission Commander (V5)  — orchestrates all of the above

Usage (inside Docker container):
  source /tmp/build/install/setup.bash
  ros2 launch agri_hexacopter full_autonomy.launch.py

Optional arguments:
  survey_timeout:=120   (seconds for V1 survey phase)
  detect_timeout:=60    (seconds for V2 detection phase)
  spray_dose:=5.0       (ml per plant)
  use_sim_time:=true    (for Gazebo simulation)
=====================================================================
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:

    # ── Declare launch arguments ───────────────────────────────────────
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='Use Gazebo simulation clock')

    spray_dose_arg = DeclareLaunchArgument(
        'spray_dose', default_value='5.0',
        description='Simulated spray dose per plant (ml)')

    # ── Shared parameter list ──────────────────────────────────────────
    use_sim_time = LaunchConfiguration('use_sim_time')

    # ─────────────────────────────────────────────────────────────────
    # NODE DEFINITIONS
    # ─────────────────────────────────────────────────────────────────

    # V4a — MSF Bridge (starts first — provides /agri/odometry)
    msf_bridge_node = Node(
        package='agri_hexacopter',
        executable='msf_bridge',
        name='msf_bridge',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        emulate_tty=True,
    )

    # V4b — Path Planner (A* — needs odometry to know start position)
    path_planner_node = Node(
        package='agri_hexacopter',
        executable='path_planner',
        name='path_planner',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        emulate_tty=True,
    )

    # V2 — Thermal Monitor / The Doctor (upgraded with world coords)
    thermal_monitor_node = Node(
        package='agri_hexacopter',
        executable='thermal_monitor',
        name='thermal_monitor',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        emulate_tty=True,
    )

    # V3 — Sprayer Control / The Helper
    sprayer_node = Node(
        package='agri_hexacopter',
        executable='agri_sprayer_control',
        name='agri_sprayer_control',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        emulate_tty=True,
    )

    # V1 — Image Collector / The Explorer
    image_collector_node = Node(
        package='agri_hexacopter',
        executable='v1_image_collector',
        name='v1_image_collector',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}],
        emulate_tty=True,
    )

    # V5 — Master Mission Commander / The Super Brain
    # Delayed by 3 s to allow all other nodes to fully initialise
    mission_commander_node = TimerAction(
        period=3.0,
        actions=[
            LogInfo(msg='🧠 [V5] Master Mission Commander starting in 3s...'),
            Node(
                package='agri_hexacopter',
                executable='master_mission_commander',
                name='master_mission_commander',
                output='screen',
                parameters=[{'use_sim_time': use_sim_time}],
                emulate_tty=True,
            ),
        ],
    )

    return LaunchDescription([
        # Arguments
        use_sim_time_arg,
        spray_dose_arg,

        # Banner
        LogInfo(msg=''),
        LogInfo(msg='╔══════════════════════════════════════════════════════╗'),
        LogInfo(msg='║  🌾 5-LAYER AUTONOMOUS AGRI-UAV SYSTEM LAUNCHING  ║'),
        LogInfo(msg='╠══════════════════════════════════════════════════════╣'),
        LogInfo(msg='║  V4a MSF Bridge       → /agri/odometry              ║'),
        LogInfo(msg='║  V4b A* Path Planner  → /agri/planned_path          ║'),
        LogInfo(msg='║  V2  Thermal Monitor  → /agri/plant_health/status   ║'),
        LogInfo(msg='║  V3  Sprayer Control  → /agri/spray_command         ║'),
        LogInfo(msg='║  V1  Image Collector  → /reports/dataset/           ║'),
        LogInfo(msg='║  V5  Mission Commander→ /agri/mission/log           ║'),
        LogInfo(msg='╚══════════════════════════════════════════════════════╝'),
        LogInfo(msg=''),

        # Nodes (in dependency order)
        msf_bridge_node,
        path_planner_node,
        thermal_monitor_node,
        sprayer_node,
        image_collector_node,
        mission_commander_node,
    ])
