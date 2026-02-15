import rclpy
from rclpy.node import Node
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand, VehicleStatus

class AgriFlyLevel1(Node):
    def __init__(self):
        super().__init__('agri_fly_level1')

        # 1. Setup Publishers (Commands to Drone)
        self.offboard_control_mode_publisher = self.create_publisher(OffboardControlMode, '/fmu/in/offboard_control_mode', 10)
        self.trajectory_setpoint_publisher = self.create_publisher(TrajectorySetpoint, '/fmu/in/trajectory_setpoint', 10)
        self.vehicle_command_publisher = self.create_publisher(VehicleCommand, '/fmu/in/vehicle_command', 10)

        # 2. State variables
        self.timer = self.create_timer(0.1, self.timer_callback) # 10Hz loop
        self.offboard_setpoint_counter = 0

    def timer_callback(self):
        if self.offboard_setpoint_counter < 10:
            self.publish_offboard_control_mode()
            self.publish_trajectory_setpoint(0.0, 0.0, 0.0)
            self.offboard_setpoint_counter += 1
        elif self.offboard_setpoint_counter == 10:
            self.change_mode(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0) # Set to Offboard
            self.arm()
            self.offboard_setpoint_counter += 1
        else:
            self.publish_offboard_control_mode()
            self.publish_trajectory_setpoint(0.0, 0.0, -5.0) # Fly to 5 meters height

    def arm(self):
        self.change_mode(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
        self.get_logger().info("Arming Hexacopter...")

    def change_mode(self, command, param1, param2=0.0):
        msg = VehicleCommand()
        msg.command = command
        msg.param1 = param1
        msg.param2 = param2
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.vehicle_command_publisher.publish(msg)

    def publish_offboard_control_mode(self):
        msg = OffboardControlMode()
        msg.position = True
        msg.velocity = False
        msg.acceleration = False
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.offboard_control_mode_publisher.publish(msg)

    def publish_trajectory_setpoint(self, x, y, z):
        msg = TrajectorySetpoint()
        msg.position = [x, y, z]
        msg.yaw = 1.57 # 90 degrees
        msg.timestamp = int(self.get_clock().now().nanoseconds / 1000)
        self.trajectory_setpoint_publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = AgriFlyLevel1()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()