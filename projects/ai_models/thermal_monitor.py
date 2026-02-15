#!/usr/bin/env python3
"""
thermal_monitor.py - Bihar-Scan AI Disease Detection Node
Simulates MobileNetV2-based thermal crop health monitoring for precision agriculture.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np

class ThermalMonitor(Node):
    def __init__(self):
        super().__init__('thermal_monitor')
        
        # QoS Profile for sensor data
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # CV Bridge for image conversion
        self.bridge = CvBridge()
        
        # Subscriber to thermal camera
        self.thermal_sub = self.create_subscription(
            Image,
            '/agri/thermal/image_raw',
            self.thermal_callback,
            qos_profile
        )
        
        # Publisher for crop health alerts
        self.alert_pub = self.create_publisher(
            String,
            '/agri/crop_health/alerts',
            10
        )
        
        # Detection parameters (simulating MobileNetV2 thresholds)
        self.hotspot_threshold = 200  # Pixel intensity (0-255 for L8 format)
        self.min_cluster_size = 50    # Minimum pixels to trigger alert
        self.frame_count = 0
        self.detection_count = 0
        
        self.get_logger().info('🌾 Bihar-Scan Thermal Monitor Initialized')
        self.get_logger().info(f'📊 Hotspot Threshold: {self.hotspot_threshold}/255')
        self.get_logger().info(f'📊 Min Cluster Size: {self.min_cluster_size} pixels')
    
    def thermal_callback(self, msg):
        """Process thermal image and detect disease hotspots"""
        try:
            # Convert ROS Image to numpy array
            thermal_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='mono8')
            
            self.frame_count += 1
            
            # Disease Detection Algorithm (Simulated MobileNetV2)
            # Step 1: Threshold for high-temperature pixels
            hotspot_mask = thermal_image > self.hotspot_threshold
            
            # Step 2: Count hotspot pixels (cluster analysis)
            hotspot_pixels = np.sum(hotspot_mask)
            
            # Step 3: Trigger alert if cluster exceeds minimum size
            if hotspot_pixels >= self.min_cluster_size:
                self.detection_count += 1
                
                # Calculate detection confidence (simulated)
                confidence = min(100.0, (hotspot_pixels / (thermal_image.size * 0.1)) * 100)
                
                # Get hotspot centroid for location reporting
                y_coords, x_coords = np.where(hotspot_mask)
                if len(y_coords) > 0:
                    centroid_x = int(np.mean(x_coords))
                    centroid_y = int(np.mean(y_coords))
                    
                    # Publish alert
                    alert_msg = String()
                    alert_msg.data = (
                        f"🚨 DISEASE HOTSPOT DETECTED | "
                        f"Frame: {self.frame_count} | "
                        f"Confidence: {confidence:.1f}% | "
                        f"Cluster Size: {hotspot_pixels} px | "
                        f"Location: ({centroid_x}, {centroid_y}) | "
                        f"Total Detections: {self.detection_count}"
                    )
                    self.alert_pub.publish(alert_msg)
                    
                    self.get_logger().warn(alert_msg.data)
            
            # Periodic status update (every 30 frames)
            if self.frame_count % 30 == 0:
                self.get_logger().info(
                    f'📸 Processed {self.frame_count} frames | '
                    f'Detections: {self.detection_count} | '
                    f'Max Temp: {np.max(thermal_image)}/255'
                )
                
        except Exception as e:
            self.get_logger().error(f'Error processing thermal image: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = ThermalMonitor()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 Thermal Monitor shutting down')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
