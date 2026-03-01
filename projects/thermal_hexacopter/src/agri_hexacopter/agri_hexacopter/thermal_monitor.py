#!/usr/bin/env python3
"""
thermal_monitor.py — Layer 2 (V2): The Doctor (UPGRADED)
=====================================================================
PURPOSE (Kid Translation):
  "The drone looks at the thermal picture and finds the 'sad hot' patches
  — plants with fever. But now, instead of just yelling 'IT'S HERE!',
  the Doctor writes a proper prescription: Plant #7 has a fever, and it
  lives at position X=12.3, Y=8.5 in the field. The Helper (V3) reads
  that address and goes there with the medicine."

CHANGES FROM ORIGINAL thermal_monitor.py:
  [+] Subscribes to VehicleLocalPosition for real-time drone NED position
  [+] Converts thermal image centroid (pixel XY) → world NED coordinates
      using camera FoV geometry and drone altitude
  [+] Publishes PlantHealthStatus (custom msg) on /agri/plant_health/status
  [~] Keeps original String publisher on /agri/crop_health/alerts (compat.)
  [+] Severity classification: WATCH / MODERATE / CRITICAL

COORDINATE CONVERSION (pixel → world):
  Given camera FoV (60°), altitude H, image size (W×H_px):
    scale = 2 * H * tan(FoV/2) / W_px   [metres per pixel]
    world_x = drone_north - (pix_y - cx_y) * scale   (North axis)
    world_y = drone_east  + (pix_x - cx_x) * scale   (East  axis)

ROS 2 TOPICS:
  SUBSCRIBED:
    /agri/thermal/image_raw          (sensor_msgs/Image)
    /fmu/out/vehicle_local_position  (px4_msgs/VehicleLocalPosition)

  PUBLISHED:
    /agri/plant_health/status        (agri_msgs/PlantHealthStatus)  ← NEW
    /agri/crop_health/alerts         (std_msgs/String)              ← kept
=====================================================================
"""

import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import numpy as np

# PX4 messages
from px4_msgs.msg import VehicleLocalPosition

# Custom message — built from agri_msgs package
from agri_msgs.msg import PlantHealthStatus


# ─────────────────────────────────────────────────────────────────────────────
# CAMERA MODEL — matches Gazebo thermal camera plugin defaults
# ─────────────────────────────────────────────────────────────────────────────
CAMERA_HFOV_DEG  = 60.0   # Horizontal Field of View (degrees)
IMAGE_WIDTH_PX   = 320    # Expected thermal image width  (pixels)
IMAGE_HEIGHT_PX  = 240    # Expected thermal image height (pixels)

# Detection thresholds
HOTSPOT_THRESHOLD  = 200  # Pixel intensity 0-255 (L8 mono)
MIN_CLUSTER_PX     = 50   # Min pixels to trigger alert
MODERATE_CLUSTER   = 300  # Cluster threshold for MODERATE severity
CRITICAL_CLUSTER   = 800  # Cluster threshold for CRITICAL severity


# ─────────────────────────────────────────────────────────────────────────────
# NODE
# ─────────────────────────────────────────────────────────────────────────────
class ThermalMonitor(Node):
    """
    V2 — The Doctor: Upgraded thermal anomaly detector.

    Publishes world-coordinate PlantHealthStatus messages for every
    detected thermal hotspot, enabling V3 (Sprayer) and V4 (Path Planner)
    to navigate directly to affected crops.
    """

    def __init__(self):
        super().__init__('thermal_monitor')

        # ── QoS ───────────────────────────────────────────────────────
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # ── State ─────────────────────────────────────────────────────
        self.bridge          = CvBridge()
        self.frame_count     = 0
        self.detection_count = 0
        self.plant_id        = 0          # Monotonically incrementing

        # Drone position (updated from VehicleLocalPosition)
        self.drone_north = 0.0
        self.drone_east  = 0.0
        self.drone_alt_m = 5.0           # Metres above ground (positive)

        # Pre-compute pixel scale (metres per pixel) for current altitude
        self._update_pixel_scale()

        # ── Subscribers ───────────────────────────────────────────────
        self.thermal_sub = self.create_subscription(
            Image, '/agri/thermal/image_raw',
            self._thermal_callback, sensor_qos)

        self.pos_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self._pos_callback, px4_qos)

        # ── Publishers ────────────────────────────────────────────────
        # V2 NEW: structured world-coordinate health status
        self.health_pub = self.create_publisher(
            PlantHealthStatus, '/agri/plant_health/status', 10)

        # Backward-compat: original string alerts
        self.alert_pub = self.create_publisher(
            String, '/agri/crop_health/alerts', 10)

        self.get_logger().info('🌡️  V2 Thermal Monitor (The Doctor) — ONLINE')
        self.get_logger().info(
            f'📊 Threshold: {HOTSPOT_THRESHOLD}/255 | '
            f'Min cluster: {MIN_CLUSTER_PX} px | '
            f'Camera FoV: {CAMERA_HFOV_DEG}°')

    # ──────────────────────────────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────────────────────────────
    def _pos_callback(self, msg: VehicleLocalPosition) -> None:
        """Update drone world position. Z in NED (negative = up)."""
        self.drone_north = msg.x
        self.drone_east  = msg.y
        # Convert NED-down to altitude-above-ground (positive)
        self.drone_alt_m = max(0.1, -msg.z)
        self._update_pixel_scale()

    def _thermal_callback(self, msg: Image) -> None:
        """
        Main detection pipeline: thermal image → PlantHealthStatus.

        Pipeline:
          1. Decode mono8 image
          2. Threshold for high-temperature pixels (hotspots)
          3. Connected-component / centroid extraction
          4. Convert centroid pixels → world NED coordinates
          5. Classify severity and publish PlantHealthStatus
        """
        try:
            thermal = self.bridge.imgmsg_to_cv2(msg, 'mono8')
        except Exception as exc:
            self.get_logger().error(f'imgmsg_to_cv2 failed: {exc}')
            return

        self.frame_count += 1
        h_px, w_px = thermal.shape

        # ── Step 1: Threshold ─────────────────────────────────────────
        hotspot_mask = thermal > HOTSPOT_THRESHOLD
        hotspot_px   = int(np.sum(hotspot_mask))

        if hotspot_px < MIN_CLUSTER_PX:
            if self.frame_count % 30 == 0:
                self.get_logger().info(
                    f'📸 Frame {self.frame_count} | healthy | '
                    f'max_temp={int(np.max(thermal))}/255')
            return

        # ── Step 2: Centroid ──────────────────────────────────────────
        y_coords, x_coords = np.where(hotspot_mask)
        cx_px = int(np.mean(x_coords))
        cy_px = int(np.mean(y_coords))

        # ── Step 3: Pixel → World coordinate conversion ───────────────
        # Image centre in pixels
        img_cx = w_px / 2.0
        img_cy = h_px / 2.0

        # Offset from image centre (positive right, positive down in image)
        delta_px_east  =  (cx_px - img_cx)
        delta_px_north = -(cy_px - img_cy)   # image Y flipped vs NED North

        world_x = self.drone_north + delta_px_north * self.m_per_px
        world_y = self.drone_east  + delta_px_east  * self.m_per_px
        world_z = -self.drone_alt_m  # NED: keep altitude of spray approach

        # ── Step 4: Severity classification ───────────────────────────
        if hotspot_px >= CRITICAL_CLUSTER:
            severity = PlantHealthStatus.SEVERITY_CRITICAL
            sev_str  = 'CRITICAL'
        elif hotspot_px >= MODERATE_CLUSTER:
            severity = PlantHealthStatus.SEVERITY_MODERATE
            sev_str  = 'MODERATE'
        else:
            severity = PlantHealthStatus.SEVERITY_WATCH
            sev_str  = 'WATCH'

        confidence = float(min(1.0, hotspot_px / (thermal.size * 0.1)))
        hotspot_intensity = int(np.max(thermal[hotspot_mask]))

        # ── Step 5: Build & publish PlantHealthStatus ─────────────────
        self.detection_count += 1
        self.plant_id        += 1

        status_msg = PlantHealthStatus()
        status_msg.header.stamp    = self.get_clock().now().to_msg()
        status_msg.header.frame_id = 'map'
        status_msg.plant_id        = self.plant_id
        status_msg.world_x         = world_x
        status_msg.world_y         = world_y
        status_msg.world_z         = world_z
        status_msg.image_pixel_x   = cx_px
        status_msg.image_pixel_y   = cy_px
        status_msg.confidence      = confidence
        status_msg.severity        = severity
        status_msg.hotspot_intensity = hotspot_intensity
        status_msg.cluster_size_px   = hotspot_px
        status_msg.description = (
            f'[{sev_str}] Plant#{self.plant_id} | '
            f'World=({world_x:.2f}N, {world_y:.2f}E) | '
            f'Conf={confidence*100:.1f}% | '
            f'Cluster={hotspot_px}px'
        )

        self.health_pub.publish(status_msg)

        # ── Backward-compat String alert ──────────────────────────────
        alert = String()
        alert.data = (
            f'🚨 DISEASE HOTSPOT [{sev_str}] | '
            f'Frame={self.frame_count} | '
            f'Plant#{self.plant_id} | '
            f'Confidence={confidence*100:.1f}% | '
            f'Cluster={hotspot_px}px | '
            f'Location=({cx_px}px, {cy_px}px) | '
            f'World=({world_x:.2f}N, {world_y:.2f}E) | '
            f'Detections={self.detection_count}'
        )
        self.alert_pub.publish(alert)
        self.get_logger().warn(alert.data)

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────
    def _update_pixel_scale(self) -> None:
        """Recompute metres-per-pixel whenever altitude changes."""
        hfov_rad      = math.radians(CAMERA_HFOV_DEG)
        ground_width  = 2.0 * self.drone_alt_m * math.tan(hfov_rad / 2.0)
        self.m_per_px = ground_width / IMAGE_WIDTH_PX


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = ThermalMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 V2 Thermal Monitor shutting down')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
