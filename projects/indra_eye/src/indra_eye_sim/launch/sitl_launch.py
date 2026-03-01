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
    
    return LaunchDescription([
        # PX4 SITL with Gazebo Garden (Bihar Hexacopter Mission)
        ExecuteProcess(
            cmd=['make', 'px4_sitl', 'gz_standard_vtol'],
            cwd=os.path.expanduser('~/PX4-Autopilot'),
            env={
                **os.environ,
                'PX4_GZ_WORLD': 'bihar_maize',
                'PX4_GZ_MODEL': 'agri_hexacopter_drone',
                'PX4_GZ_MODEL_POSE': '0,0,1,0,0,0',
                'PX4_GZ_STANDALONE': '1',
                'PX4_HOME_LAT': '25.344644',
                'PX4_HOME_LON': '86.483958',
                'PX4_HOME_ALT': '50.0',
                'GZ_IP': '127.0.0.1',
                'GZ_PARTITION': 'indra_eye_sim',
                'GZ_SIM_RENDER_ENGINE_TYPE': 'ogre',
                'GZ_SIM_RESOURCE_PATH': ':'.join([
                    os.path.expanduser('~/uav_master_hub/assets/models'),
                    os.path.expanduser('~/uav_master_hub/assets/worlds'),
                    os.path.expanduser('~/PX4-Autopilot/Tools/simulation/gz/models'),
                    os.path.expanduser('~/PX4-Autopilot/Tools/simulation/gz/worlds'),
                ])
            },
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
                'publish_rate_hz': 100.0,
                'visual_weight': 5.0
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
        
        # MAVROS Bridge Node (publishes /px4/imu and /px4/gnss for ES-EKF)
        Node(
            package='indra_eye_core',
            executable='mavros_bridge_node',
            name='mavros_bridge_node',
            output='screen',
            parameters=[{
                'mavlink_port': 14580,
                'target_system_id': 1
            }]
        ),

        # RViz for visualization (requires X11 display)
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', os.path.join(sim_pkg, 'rviz', 'indra_eye.rviz')],
            output='screen'
        ),
    ])
