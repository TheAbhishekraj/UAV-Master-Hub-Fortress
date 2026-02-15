#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleStatus

class HeartbeatListener(Node):
    def __init__(self):
        super().__init__('heartbeat_listener')
        
        # Subscribe to the Drone's Status
        self.subscription = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status',
            self.listener_callback,
            10)
        print("Waiting for Drone Connection... (Make sure Micro XRCE-DDS is running!)")

    def listener_callback(self, msg):
        # If we hear the drone, print the Magic Green Check
        print(f"\n✅ CONNECTION VERIFIED!")
        print(f"   Drone ID: {msg.system_id} | Component: {msg.component_id}")
        print(f"   Nav State: {msg.nav_state}")
        # Exit once verified so we don't spam the logs
        raise SystemExit

def main(args=None):
    rclpy.init(args=args)
    heartbeat_node = HeartbeatListener()

    try:
        rclpy.spin(heartbeat_node)
    except SystemExit:
        print("Test Passed. Closing node.")
    except Exception as e:
        pass
    finally:
        heartbeat_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
