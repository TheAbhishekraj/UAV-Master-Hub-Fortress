#!/usr/bin/env python3
"""
v1_image_collector.py — Layer 1 (V1): The Explorer
=====================================================================
PURPOSE (Kid Translation):
  "The drone flies over the cornfield like a lawn mower in the sky —
  row by row — and takes pictures with both its normal camera AND its
  heat-vision camera. Every photo is saved with a label that says
  exactly WHERE the drone was standing when it took the picture. This
  builds a map of the whole farm that the Doctor (V2) will study later."

TECHNICAL SUMMARY:
  - Subscribes to RGB camera and Thermal camera image topics
  - Subscribes to vehicle_local_position for NED position tagging
  - Executes an automated lawnmower survey waypoint grid over the
    bihar_maize Gazebo world (20m × 20m, rows 5m apart, altitude 5m)
  - Publishes TrajectorySetpoint commands via PX4 offboard mode
  - Saves timestamped PNG images to /reports/dataset/{rgb,thermal}/

ROS 2 TOPICS:
  SUBSCRIBED:
    /agri/camera/image_raw      (sensor_msgs/Image)   — RGB camera
    /agri/thermal/image_raw     (sensor_msgs/Image)   — Thermal camera
    /fmu/out/vehicle_local_position  (px4_msgs/VehicleLocalPosition)

  PUBLISHED:
    /fmu/in/offboard_control_mode  (px4_msgs/OffboardControlMode)
    /fmu/in/trajectory_setpoint    (px4_msgs/TrajectorySetpoint)
    /fmu/in/vehicle_command        (px4_msgs/VehicleCommand)
    /agri/v1/status                (std_msgs/String)   — mission log

ARCHITECTURE CONSTRAINT:
  Built in /tmp/build inside the Docker container.
  Output images written to the volume-mounted /reports/dataset/ path.
=====================================================================
"""

import os
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

# ROS 2 messages
from sensor_msgs.msg import Image
from std_msgs.msg import String
from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
    VehicleStatus,
)

# Image saving
try:
    from cv_bridge import CvBridge
    import cv2
    _CV_AVAILABLE = True
except ImportError:
    _CV_AVAILABLE = False

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION — Bihar Maize Survey Grid
# ─────────────────────────────────────────────────────────────────────────────
SURVEY_ALTITUDE_M  = -5.0     # NED: negative = up
FIELD_WIDTH_M      = 20.0     # East extent of bihar_maize.sdf
FIELD_HEIGHT_M     = 20.0     # North extent
ROW_SPACING_M      = 5.0      # Distance between lawnmower rows
WAYPOINT_TOLERANCE = 1.0      # Metres: "close enough" to advance
HOVER_TICKS        = 30       # Ticks (@ 10 Hz) to hover at each WP
OUTPUT_BASE        = "/reports/dataset"   # Volume-mounted reports dir
SAVE_EVERY_N_FRAMES = 10      # Save 1 image per N frames at each WP


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY: Generate lawnmower waypoints
# ─────────────────────────────────────────────────────────────────────────────
def generate_survey_grid(
    width: float = FIELD_WIDTH_M,
    height: float = FIELD_HEIGHT_M,
    row_spacing: float = ROW_SPACING_M,
    altitude: float = SURVEY_ALTITUDE_M,
) -> list:
    """
    Generate NED-frame lawnmower waypoints.

    Returns list of [N, E, D] positions covering the field in a
    boustrophedon (back-and-forth) pattern.

    Pattern visualised (top-down):
        → → → → →
                 ↓
        ← ← ← ← ←
        ↓
        → → → → →
    """
    waypoints = []
    row_count = int(height / row_spacing) + 1
    for row_idx in range(row_count):
        north = row_idx * row_spacing
        if row_idx % 2 == 0:   # Left to right
            east_start, east_end = 0.0, width
        else:                   # Right to left (boustrophedon)
            east_start, east_end = width, 0.0
        waypoints.append([north, east_start, altitude])
        waypoints.append([north, east_end,   altitude])
    return waypoints


# ─────────────────────────────────────────────────────────────────────────────
# NODE
# ─────────────────────────────────────────────────────────────────────────────
class V1ImageCollector(Node):
    """
    V1 — The Explorer: Autonomous survey + image dataset builder.

    State machine:
        INIT → ARM_AND_OFFBOARD → TAKEOFF → SURVEY → RTL → LAND → DONE
    """

    def __init__(self):
        super().__init__('v1_image_collector')

        # ── QoS profiles ──────────────────────────────────────────────
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # ── Publishers ────────────────────────────────────────────────
        self.offboard_pub = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', px4_qos)
        self.traj_pub = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', px4_qos)
        self.cmd_pub = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', px4_qos)
        self.status_pub = self.create_publisher(
            String, '/agri/v1/status', 10)

        # ── Subscribers ───────────────────────────────────────────────
        self.rgb_sub = self.create_subscription(
            Image, '/agri/camera/image_raw',
            self._rgb_callback, sensor_qos)
        self.thermal_sub = self.create_subscription(
            Image, '/agri/thermal/image_raw',
            self._thermal_callback, sensor_qos)
        self.pos_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self._pos_callback, px4_qos)
        self.status_sub = self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status',
            self._vehicle_status_callback, px4_qos)

        # ── State ─────────────────────────────────────────────────────
        self.state           = 'INIT'
        self.tick            = 0
        self.wp_index        = 0
        self.hover_tick      = 0
        self.image_count     = 0
        self.rgb_frame_count = 0
        self.thm_frame_count = 0

        self.pos_x  = 0.0    # North (m)
        self.pos_y  = 0.0    # East  (m)
        self.pos_z  = 0.0    # Down  (m, negative = up)

        self.current_rgb     : Image | None = None
        self.current_thermal : Image | None = None
        self.arming_state    = 0
        self.nav_state       = 0

        # ── Dataset directories ───────────────────────────────────────
        self._ensure_dirs()

        # ── CV Bridge ─────────────────────────────────────────────────
        self.bridge = CvBridge() if _CV_AVAILABLE else None

        # ── Survey waypoints ─────────────────────────────────────────
        self.waypoints = generate_survey_grid()
        self.get_logger().info(
            f'📸 V1 Image Collector ready | '
            f'{len(self.waypoints)} survey waypoints generated')
        self._log(f'Survey grid: {len(self.waypoints)} waypoints over '
                  f'{FIELD_WIDTH_M}m × {FIELD_HEIGHT_M}m field')

        # ── 10 Hz control loop ────────────────────────────────────────
        self.timer = self.create_timer(0.1, self._tick)

    # ──────────────────────────────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────────────────────────────
    def _rgb_callback(self, msg: Image) -> None:
        self.current_rgb = msg
        self.rgb_frame_count += 1

    def _thermal_callback(self, msg: Image) -> None:
        self.current_thermal = msg
        self.thm_frame_count += 1

    def _pos_callback(self, msg: VehicleLocalPosition) -> None:
        self.pos_x = msg.x
        self.pos_y = msg.y
        self.pos_z = msg.z

    def _vehicle_status_callback(self, msg: VehicleStatus) -> None:
        self.arming_state = msg.arming_state
        self.nav_state    = msg.nav_state

    # ──────────────────────────────────────────────────────────────────
    # Main 10 Hz loop — state machine
    # ──────────────────────────────────────────────────────────────────
    def _tick(self) -> None:
        self.tick += 1
        self._publish_offboard_keepalive()

        if self.state == 'INIT':
            if self.tick == 20:   # Give PX4 2 s to boot
                self._arm_and_offboard()
                self.state = 'ARM_AND_OFFBOARD'

        elif self.state == 'ARM_AND_OFFBOARD':
            if self.tick > 30:
                self.state = 'TAKEOFF'
                self._log('🚁 Takeoff initiated')

        elif self.state == 'TAKEOFF':
            self._goto([0.0, 0.0, SURVEY_ALTITUDE_M])
            if abs(self.pos_z - SURVEY_ALTITUDE_M) < WAYPOINT_TOLERANCE:
                self.state = 'SURVEY'
                self._log(f'✅ At survey altitude {abs(SURVEY_ALTITUDE_M):.0f} m. '
                          'Starting lawnmower survey.')

        elif self.state == 'SURVEY':
            if self.wp_index >= len(self.waypoints):
                self.state = 'RTL'
                self._log(f'🏁 Survey complete. '
                          f'Collected {self.image_count} image pairs. RTL.')
                return

            target = self.waypoints[self.wp_index]
            self._goto(target)

            if self._at_waypoint(target):
                self.hover_tick += 1
                if self.hover_tick % SAVE_EVERY_N_FRAMES == 0:
                    self._save_image_pair()

                if self.hover_tick >= HOVER_TICKS:
                    self.hover_tick = 0
                    self.wp_index  += 1
                    if self.wp_index < len(self.waypoints):
                        self._log(f'📍 WP {self.wp_index}/{len(self.waypoints)} reached. '
                                  f'Advancing.')

        elif self.state == 'RTL':
            self._goto([0.0, 0.0, SURVEY_ALTITUDE_M])
            if self._at_waypoint([0.0, 0.0, SURVEY_ALTITUDE_M]):
                self.state = 'LAND'
                self._send_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
                self._log('🛬 Landing...')

        elif self.state == 'LAND':
            if self.tick % 100 == 0:
                self._log('⏳ Waiting for landing confirmation...')
            if abs(self.pos_z) < 0.3:    # Near ground
                self.state = 'DONE'
                self._log('✅ V1 Mission COMPLETE.')
                self.timer.cancel()

    # ──────────────────────────────────────────────────────────────────
    # PX4 Command Helpers
    # ──────────────────────────────────────────────────────────────────
    def _publish_offboard_keepalive(self) -> None:
        msg = OffboardControlMode()
        msg.position     = True
        msg.velocity     = False
        msg.acceleration = False
        msg.attitude     = False
        msg.body_rate    = False
        msg.timestamp    = self._now()
        self.offboard_pub.publish(msg)

    def _goto(self, ned: list) -> None:
        msg = TrajectorySetpoint()
        msg.position  = [float(ned[0]), float(ned[1]), float(ned[2])]
        msg.yaw       = 0.0          # Face north
        msg.timestamp = self._now()
        self.traj_pub.publish(msg)

    def _arm_and_offboard(self) -> None:
        self._send_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
        self._send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
        self._log('🔑 ARM + OFFBOARD commands sent')

    def _send_vehicle_command(self, cmd, p1=0.0, p2=0.0) -> None:
        msg = VehicleCommand()
        msg.command          = cmd
        msg.param1           = float(p1)
        msg.param2           = float(p2)
        msg.target_system    = 1
        msg.target_component = 1
        msg.source_system    = 1
        msg.source_component = 1
        msg.from_external    = True
        msg.timestamp        = self._now()
        self.cmd_pub.publish(msg)

    def _at_waypoint(self, ned: list) -> bool:
        dist = math.sqrt(
            (self.pos_x - ned[0]) ** 2 +
            (self.pos_y - ned[1]) ** 2 +
            (self.pos_z - ned[2]) ** 2
        )
        return dist < WAYPOINT_TOLERANCE

    # ──────────────────────────────────────────────────────────────────
    # Image saving
    # ──────────────────────────────────────────────────────────────────
    def _save_image_pair(self) -> None:
        """Save one RGB + one Thermal image tagged with position."""
        ts   = self.get_clock().now().nanoseconds
        tag  = f'{ts}__N{self.pos_x:.1f}_E{self.pos_y:.1f}'

        saved_rgb  = self._save_image(self.current_rgb,
                                      os.path.join(OUTPUT_BASE, 'rgb'),
                                      f'RGB_{tag}.png')
        saved_thm  = self._save_image(self.current_thermal,
                                      os.path.join(OUTPUT_BASE, 'thermal'),
                                      f'THERMAL_{tag}.png')

        if saved_rgb or saved_thm:
            self.image_count += 1
            self._log(f'💾 Saved pair #{self.image_count} at '
                      f'N={self.pos_x:.1f} E={self.pos_y:.1f} '
                      f'Z={self.pos_z:.1f}')

    def _save_image(self, ros_img: Image | None,
                    directory: str, filename: str) -> bool:
        if ros_img is None or not _CV_AVAILABLE:
            return False
        try:
            encoding = ros_img.encoding if ros_img.encoding else 'bgr8'
            if encoding == 'mono8':
                cv_img = self.bridge.imgmsg_to_cv2(ros_img, 'mono8')
            else:
                cv_img = self.bridge.imgmsg_to_cv2(ros_img, 'bgr8')
            path = os.path.join(directory, filename)
            cv2.imwrite(path, cv_img)
            return True
        except Exception as exc:
            self.get_logger().warn(f'Image save failed: {exc}')
            return False

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────
    def _ensure_dirs(self) -> None:
        for sub in ('rgb', 'thermal'):
            path = os.path.join(OUTPUT_BASE, sub)
            os.makedirs(path, exist_ok=True)

    def _log(self, msg: str) -> None:
        self.get_logger().info(msg)
        self.status_pub.publish(String(data=f'[V1] {msg}'))

    def _now(self) -> int:
        return int(self.get_clock().now().nanoseconds / 1000)


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = V1ImageCollector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 V1 Image Collector interrupted')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
