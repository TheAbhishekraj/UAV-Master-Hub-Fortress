import os
import datetime
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.actions import Node

def generate_launch_description():
    """
    UAV Master Hub Fortress v4.0 - Unified Launch Engine (Split-Launch)
    Bypasses bridge timeouts by decoupling Gazebo Server, Model Spawner, and PX4 Standalone.
    """
    
    # Base Environment Configuration
    px4_env = os.environ.copy()
    px4_env['PX4_GZ_WORLD'] = 'bihar_maize'
    px4_env['PX4_GZ_MODEL'] = 'agri_hexacopter_drone'
    px4_env['PX4_GZ_MODEL_POSE'] = '0,0,0.5,0,0,0'
    px4_env['PX4_HOME_LAT'] = '25.344644'
    px4_env['PX4_HOME_LON'] = '86.483958'
    px4_env['PX4_HOME_ALT'] = '50.0'
    px4_env['GZ_SIM_RESOURCE_PATH'] = '/root/uav_master_hub/assets/models:/root/uav_master_hub/assets/worlds:/root/PX4-Autopilot/Tools/simulation/gz/models'
    px4_env['GZ_PARTITION'] = 'indra_eye_sim'
    px4_env['DISPLAY'] = ':0'
    px4_env['QT_X11_NO_MITSHM'] = '1'

    # 1. Start Gazebo Server with the Bihar Maize World directly
    gz_server = ExecuteProcess(
        cmd=['gz', 'sim', '-s', '-r', '/root/PX4-Autopilot/Tools/simulation/gz/worlds/bihar_maize.sdf'],
        env=px4_env,
        name='gz_server',
        output='screen'
    )

    # 2. Start DDS Bridge
    xrce_agent = ExecuteProcess(
        cmd=['MicroXRCEAgent', 'udp4', '-p', '8888'],
        name='microxrce_agent',
        output='screen'
    )

    # 3. Manually Spawn the Drone (Bypasses Spawner Timeout)
    spawn_cmd = [
        'gz', 'service', '-s', '/world/bihar_maize/create',
        '--reqtype', 'gz.msgs.EntityFactory',
        '--reptype', 'gz.msgs.Boolean',
        '--timeout', '10000',
        '--req', "sdf_filename: '/root/uav_master_hub/assets/models/agri_hexacopter_drone/model.sdf', name: 'agri_hexacopter_drone', pose: {position: {z: 0.5}}"
    ]
    gz_spawn = ExecuteProcess(
        cmd=spawn_cmd,
        env=px4_env,
        name='gz_spawner',
        output='screen'
    )

    # 4. Start PX4 in STANDALONE mode
    px4_env_standalone = px4_env.copy()
    px4_env_standalone['PX4_GZ_STANDALONE'] = '1'
    px4_sitl = ExecuteProcess(
        cmd=['make', 'px4_sitl', 'gz_standard_vtol'],
        cwd='/root/PX4-Autopilot',
        env=px4_env_standalone,
        name='px4_sitl',
        output='screen'
    )

    # 5. Start Gazebo GUI 
    gz_gui = ExecuteProcess(
        cmd=['gz', 'sim', '-g'],
        env=px4_env,
        name='gz_gui',
        output='screen'
    )

    # 6. ES-EKF and Mission Commander
    es_ekf_node = Node(
        package='indra_eye_core',
        executable='es_ekf_node',
        name='es_ekf',
        output='screen'
    )
    
    v5_mission_commander = Node(
        package='agri_hexacopter',
        executable='master_mission_commander',
        name='v5_commander',
        output='screen'
    )

    # 7. Evidence Recorder
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    bag_path = f"/tmp/fortress_evidence/golden_bag_{timestamp}"
    rosbag_recorder = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'record',
            '-o', bag_path,
            '/indra_eye/diagnostics',
            '/agri/mission/log',
            '/fmu/out/vehicle_gps_position',
            '/fmu/out/vehicle_local_position'
        ],
        name='golden_recorder',
        output='screen'
    )

    # STAGED EXECUTION
    # 0s: Server + DDS
    # 5s: Spawn Drone + GUI
    # 10s: PX4 Standalone
    # 15s: EKF Node
    # 20s: V5 + Recorder
    return LaunchDescription([
        gz_server,
        xrce_agent,
        TimerAction(period=5.0, actions=[gz_spawn, gz_gui]),
        TimerAction(period=10.0, actions=[px4_sitl]),
        TimerAction(period=15.0, actions=[es_ekf_node]),
        TimerAction(period=20.0, actions=[v5_mission_commander, rosbag_recorder])
    ])
