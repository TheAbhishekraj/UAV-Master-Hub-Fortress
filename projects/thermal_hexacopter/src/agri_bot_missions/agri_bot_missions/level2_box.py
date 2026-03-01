#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy

from px4_msgs.msg import OffboardControlMode
from px4_msgs.msg import TrajectorySetpoint
from px4_msgs.msg import VehicleCommand
from px4_msgs.msg import VehicleStatus

class Level2Box(Node):
    def __init__(self):
        super().__init__('level2_box')
        
        # QoS Profile
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        # Publishers
        self.offboard_control_mode_publisher_ = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', qos_profile)
        self.trajectory_setpoint_publisher_ = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', qos_profile)
        self.vehicle_command_publisher_ = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', qos_profile)

        # Subscribers
        self.vehicle_status_subscriber_ = self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status', self.vehicle_status_callback, qos_profile)

        # Variables
        self.vehicle_status = VehicleStatus()
        self.offboard_setpoint_counter_ = 0
        self.mission_state = 'INIT'
        self.altitude = -5.0 # NED
        
        # Waypoints for 10x10m box
        self.waypoints = {
            'TAKEOFF': [0.0, 0.0, self.altitude],
            'WP1': [10.0, 0.0, self.altitude],      # 10m North
            'WP2': [10.0, 10.0, self.altitude],     # 10m North, 10m East
            'WP3': [0.0, 10.0, self.altitude],      # 10m East
            'RETURN': [0.0, 0.0, self.altitude]     # Return Home
        }
        self.current_target = self.waypoints['TAKEOFF']

        # Timer
        self.timer_ = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info("🚀 Level 2: Box Mission Initialized")

    def vehicle_status_callback(self, msg):
        self.vehicle_status = msg

    def timer_callback(self):
        # Arm & Offboard Logic
        if self.offboard_setpoint_counter_ == 10:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1., 6.)
            self.arm()
            self.mission_state = 'TAKEOFF'

        self.publish_offboard_control_mode()

        if self.mission_state == 'LAND':
            pass # Keep publishing offboard mode, but let land command take over? 
                 # Actually better to invoke land command ONCE and maybe stop offboard setpoints?
                 # PX4 handles landing in Land mode. We can stop sending setpoints or keep sending current position.
        else:
            self.publish_trajectory_setpoint()
            self.check_mission_progress()

        if self.offboard_setpoint_counter_ < 11:
            self.offboard_setpoint_counter_ += 1
        
        # Using a separate tick counter for mission progress would be safer if we want to cap setpoints
        # But here we just need to increment regardless
        # Let's add a mission_tick counter
        if not hasattr(self, 'mission_tick'):
            self.mission_tick = 0
        self.mission_tick += 1

    def check_mission_progress(self):
        # Simplified time-based state machine for robustness in simulation
        # In real world, use odometry distance check
        
        # Assuming ~10Hz loop
        # Takeoff: 5s
        # WP1: 10s (travel 10m)
        # WP2: 10s
        # WP3: 10s
        # Return: 10s
        # Land: > 45s
        
        # Using tick count for timing
        current_tick = getattr(self, 'mission_tick', 0)
        
        if current_tick < 50: # 5s
            self.mission_state = 'TAKEOFF'
            self.current_target = self.waypoints['TAKEOFF']
        elif current_tick < 150: # 15s (10s for leg 1)
            self.mission_state = 'WP1'
            self.current_target = self.waypoints['WP1']
            if current_tick == 50: self.get_logger().info(f"Stats: WP1 -> {self.current_target}")
        elif current_tick < 250: # 25s
            self.mission_state = 'WP2'
            self.current_target = self.waypoints['WP2']
            if current_tick == 150: self.get_logger().info(f"Stats: WP2 -> {self.current_target}")
        elif current_tick < 350: # 35s
            self.mission_state = 'WP3'
            self.current_target = self.waypoints['WP3']
            if current_tick == 250: self.get_logger().info(f"Stats: WP3 -> {self.current_target}")
        elif current_tick < 450: # 45s
            self.mission_state = 'RETURN'
            self.current_target = self.waypoints['RETURN']
            if current_tick == 350: self.get_logger().info(f"Stats: RETURN -> {self.current_target}")
        else:
            self.mission_state = 'LAND'
            if current_tick == 450:
                self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
                self.get_logger().info("🛬 Mission Complete. Landing...")

    def arm(self):
        self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
        self.get_logger().info("🚀 Arm command sent")

    def publish_offboard_control_mode(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_control_mode_publisher_.publish(msg)

    def publish_trajectory_setpoint(self):
        msg = TrajectorySetpoint()
        msg.position = self.current_target
        msg.yaw = -3.14 # Face North
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_setpoint_publisher_.publish(msg)

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.param1 = param1
        msg.param2 = param2
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = Level2Box()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()