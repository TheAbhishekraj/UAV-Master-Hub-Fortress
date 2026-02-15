"""
Indra-Eye SITL Launch File

Launches complete simulation stack:
- Gazebo with Himalayan terrain
- PX4 SITL
- ES-EKF node
- Supervisor node
- RViz visualization
"""

from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Package directories
    sim_pkg = get_package_share_directory('indra_eye_sim')
    
    # Gazebo world file
    world_file = os.path.join(sim_pkg, 'worlds', 'himalayan_terrain.world')
    
    return LaunchDescription([
        # Gazebo server
        ExecuteProcess(
            cmd=['gzserver', '--verbose', world_file],
            output='screen',
            name='gazebo_server'
        ),
        
        # Gazebo client (GUI)
        ExecuteProcess(
            cmd=['gzclient'],
            output='screen',
            name='gazebo_client'
        ),
        
        # PX4 SITL (assuming PX4-Autopilot is installed)
        ExecuteProcess(
            cmd=['make', 'px4_sitl', 'gazebo'],
            cwd=os.path.expanduser('~/PX4-Autopilot'),
            output='screen',
            name='px4_sitl'
        ),
        
        # MicroXRCE-DDS Agent (PX4 <-> ROS 2 bridge)
        ExecuteProcess(
            cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
            output='screen',
            name='micro_xrce_agent'
        ),
        
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
            }]
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
            }]
        ),
        
        # RViz for visualization
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(sim_pkg, 'rviz', 'indra_eye.rviz')],
            output='screen'
        ),
    ])
