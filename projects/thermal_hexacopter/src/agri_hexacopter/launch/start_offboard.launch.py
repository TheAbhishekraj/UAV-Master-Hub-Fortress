import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('agri_hexacopter'),
        'config',
        'mission_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='agri_hexacopter',
            executable='mission_control',
            name='mission_control_node',
            output='screen',
            parameters=[config]
        )
    ])
