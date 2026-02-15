#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

# Standard ROS2 Messages
from geometry_msgs.msg import Point
from std_msgs.msg import String, Bool

class AgriMissionControl(Node):

    def __init__(self):
        super().__init__('agri_mission_control')
        
        # --- CONFIGURATION ---
        self.declare_parameter('flight_altitude', 3.0)
        self.target_altitude = self.get_parameter('flight_altitude').value
        
        # --- PUBLISHERS (Commands to Drone) ---
        # Simulating the Sprayer Solenoid
        self.sprayer_pub = self.create_publisher(Bool, '/agri/sprayer_active', 10)
        # Logging for the user
        self.status_pub = self.create_publisher(String, '/agri/status_log', 10)

        # --- INTERNAL STATE ---
        self.mission_step = 0
        self.timer = self.create_timer(2.0, self.mission_loop)
        
        self.print_status("🚀 SYSTEM BOOT", "Initializing Mission Control...")

    def print_status(self, tag, message):
        """Helper for professional logging with visual ticks"""
        log_msg = f"[{tag}] {message}"
        self.get_logger().info(log_msg)
        self.status_pub.publish(String(data=log_msg))

    def mission_loop(self):
        """The Main State Machine (Runs every 2 seconds)"""
        
        # PHASE 1: PRE-ARM CHECKS
        if self.mission_step == 0:
            self.print_status("✅ CHECK 1", "Battery Level: 98% (Simulated)")
            self.print_status("✅ CHECK 2", "GPS Lock: 12 Satellites Found")
            self.print_status("✅ CHECK 3", "Thermal Camera: ONLINE (32°C Ambient)")
            self.mission_step += 1

        # PHASE 2: TAKEOFF
        elif self.mission_step == 1:
            self.print_status("🚁 TAKEOFF", f"Climbing to {self.target_altitude} meters...")
            # (In real code, we send vehicle_command here)
            self.mission_step += 1

        # PHASE 3: PATH PLANNING (Waypoint 1)
        elif self.mission_step == 2:
            self.print_status("📍 WAYPOINT A", "Arrived at Maize Row 1. Scanning...")
            self.mission_step += 1

        # PHASE 4: DISEASE DETECTION & SPRAYING
        elif self.mission_step == 3:
            self.print_status("⚠️ ALERT", "Thermal Anomaly Detected! (Leaf Temp > 35°C)")
            self.print_status("💦 ACTION", "Engaging Solenoid Valve via GPIO...")
            
            # Activate Sprayer
            msg = Bool()
            msg.data = True
            self.sprayer_pub.publish(msg)
            
            self.mission_step += 1

        # PHASE 5: SPRAY COMPLETE
        elif self.mission_step == 4:
            msg = Bool()
            msg.data = False
            self.sprayer_pub.publish(msg)
            self.print_status("✅ SPRAY", "Solenoid Closed. Dosage Administered.")
            self.mission_step += 1

        # PHASE 6: RETURN TO HOME
        elif self.mission_step == 5:
            self.print_status("🏠 RTL", "Returning to Landing Pad...")
            self.mission_step += 1
            
        elif self.mission_step == 6:
            self.print_status("🏁 FINISH", "Mission Complete. System Standby.")
            self.timer.cancel() # Stop the loop

def main(args=None):
    rclpy.init(args=args)
    node = AgriMissionControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.print_status("🛑 ABORT", "Manual Override Triggered!")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
