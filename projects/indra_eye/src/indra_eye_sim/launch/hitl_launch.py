"""
Indra-Eye Hardware-in-the-Loop (HITL) Launch File

Launches real sensor drivers and Indra-Eye nodes for Jetson Orin Nano deployment.
No Gazebo simulation - uses actual hardware sensors.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os
import yaml

def generate_launch_description():
    # Launch arguments
    hardware_config_arg = DeclareLaunchArgument(
        'hardware_config',
        default_value='/home/abhishek/thermal_hexacopter_project/indra_eye_project/config/hardware_map.yaml',
        description='Path to hardware configuration file'
    )
    
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='true',
        description='Launch RViz for visualization'
    )
    
    use_qgc_arg = DeclareLaunchArgument(
        'use_qgc',
        default_value='false',
        description='Launch QGroundControl automatically'
    )
    
    # Load hardware configuration
    hardware_config_file = LaunchConfiguration('hardware_config')
    
    return LaunchDescription([
        hardware_config_arg,
        use_rviz_arg,
        use_qgc_arg,
        
        # ====================================================================
        # Sensor Drivers
        # ====================================================================
        
        # Livox Mid-360 LiDAR Driver
        Node(
            package='livox_ros_driver2',
            executable='livox_ros_driver2_node',
            name='livox_lidar_publisher',
            output='screen',
            parameters=[{
                'xfer_format': 1,
                'multi_topic': 0,
                'data_src': 0,
                'publish_freq': 10.0,
                'output_data_type': 0,
                'frame_id': 'livox_frame',
                'user_config_path': '/home/abhishek/thermal_hexacopter_project/indra_eye_project/config/livox_config.json'
            }]
        ),
        
        # Intel RealSense D435i Camera Driver
        Node(
            package='realsense2_camera',
            executable='realsense2_camera_node',
            name='realsense_camera',
            output='screen',
            parameters=[{
                'depth_module.profile': '640x480x30',
                'rgb_camera.profile': '640x480x30',
                'enable_infra1': True,
                'enable_infra2': True,
                'enable_accel': True,
                'enable_gyro': True,
                'unite_imu_method': 'linear_interpolation',
                'enable_sync': True,
                'align_depth.enable': True
            }]
        ),
        
        # u-blox F9P GNSS Driver
        Node(
            package='ublox_gps',
            executable='ublox_gps_node',
            name='ublox_gps_node',
            output='screen',
            parameters=[{
                'device': '/dev/ttyUSB0',
                'baudrate': 115200,
                'frame_id': 'gnss_link',
                'rate': 10,
                'enable_ppp': True,
                'enable_galileo': True,
                'enable_glonass': True,
                'enable_beidou': True
            }]
        ),
        
        # ====================================================================
        # Indra-Eye Core Nodes
        # ====================================================================
        
        # ES-EKF Node
        Node(
            package='indra_eye_core',
            executable='es_ekf_node',
            name='es_ekf_node',
            output='screen',
            parameters=[{
                'use_gnss': True,
                'use_vio': True,
                'use_slam': True,
                'publish_rate_hz': 100.0
            }],
            remappings=[
                ('/px4/imu', '/camera/imu'),  # Use RealSense IMU
                ('/px4/gnss', '/ublox/fix'),
                ('/lidar/slam/pose', '/slam/pose')
            ]
        ),
        
        # Supervisor Node
        Node(
            package='indra_eye_supervisor',
            executable='supervisor_node',
            name='supervisor_node',
            output='screen',
            parameters=[{
                'mahalanobis_threshold': 9.21,
                'spoofing_detection_window': 2.0,
                'gnss_timeout': 5.0
            }],
            remappings=[
                ('/px4/gnss', '/ublox/fix')
            ]
        ),
        
        # MAVROS Bridge Node
        Node(
            package='indra_eye_core',
            executable='mavros_bridge_node',
            name='mavros_bridge_node',
            output='screen',
            parameters=[{
                'home_latitude': 34.1526,   # Leh, Ladakh
                'home_longitude': 77.5771,
                'home_altitude': 3500.0
            }]
        ),
        
        # Path Aggregator Node
        Node(
            package='indra_eye_core',
            executable='path_aggregator_node',
            name='path_aggregator_node',
            output='screen',
            parameters=[{
                'max_path_length': 1000,
                'publish_rate_hz': 10.0,
                'home_latitude': 34.1526,
                'home_longitude': 77.5771,
                'home_altitude': 3500.0
            }],
            remappings=[
                ('/px4/gnss', '/ublox/fix')
            ]
        ),
        
        # ====================================================================
        # MAVROS (for PX4 communication)
        # ====================================================================
        
        # MAVROS Node
        Node(
            package='mavros',
            executable='mavros_node',
            name='mavros',
            output='screen',
            parameters=[{
                'fcu_url': 'udp://:14540@127.0.0.1:14557',  # PX4 SITL/HITL
                'gcs_url': '',
                'target_system_id': 1,
                'target_component_id': 1,
                'fcu_protocol': 'v2.0'
            }]
        ),
        
        # ====================================================================
        # Micro-XRCE-DDS Agent (PX4 <-> ROS 2 Bridge)
        # ====================================================================
        
        ExecuteProcess(
            cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
            output='screen',
            name='micro_xrce_agent'
        ),
        
        # ====================================================================
        # Visualization
        # ====================================================================
        
        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', '/home/abhishek/thermal_hexacopter_project/indra_eye_project/src/indra_eye_sim/rviz/indra_eye_mission.rviz'],
            output='screen',
            condition=IfCondition(LaunchConfiguration('use_rviz'))
        ),
        
        # QGroundControl (optional)
        ExecuteProcess(
            cmd=['qgroundcontrol'],
            output='screen',
            name='qgroundcontrol',
            condition=IfCondition(LaunchConfiguration('use_qgc'))
        ),
        
        # ====================================================================
        # Data Logging (ROS 2 Bag)
        # ====================================================================
        
        ExecuteProcess(
            cmd=[
                'ros2', 'bag', 'record',
                '-o', '/home/abhishek/thermal_hexacopter_project/indra_eye_project/logs/rosbags/hitl_mission',
                '/livox/lidar',
                '/camera/depth/image_rect_raw',
                '/camera/color/image_raw',
                '/camera/imu',
                '/ublox/fix',
                '/indra_eye/fused_odom',
                '/indra_eye/navigation_mode',
                '/indra_eye/spoofing_detected',
                '/visualization/gps_path',
                '/visualization/vio_path',
                '/visualization/fused_path'
            ],
            output='screen',
            name='rosbag_recorder'
        ),
    ])
