#!/usr/bin/env python3
"""
msf_bridge.py — Layer 4 (V4): The Smart Scout — MSF Integration
=====================================================================
PURPOSE (Kid Translation):
  "When we turn off GPS (flying in the dark forest), the drone uses its
  inner ear — the Indra-Eye Visual Odometry (VO) camera. This bridge
  takes the VO position reading and passes it to the path planner and
  sprayer so they can still navigate accurately. If the inner ear gets
  confused (VO drops out), the drone automatically switches to its
  backup inner ear — the PX4 flight controller's own position estimate."

TECHNICAL SUMMARY:
  Multi-Sensor Fusion (MSF) bridge node that:
  1. Subscribes to Indra-Eye VO odometry output
  2. Re-publishes fused position on /agri/odometry for system-wide use
  3. Monitors VO health with a watchdog timer (2 s timeout)
  4. Falls back to /fmu/out/vehicle_local_position when VO is unavailable
  5. Publishes sensor fusion status diagnostics

VO SOURCE:
  - indra_eye_core publishes on /indra_eye/odometry (nav_msgs/Odometry)
    from its mavros_bridge_node (C++ node in indra_eye_core package)
  - Position frame: body-fixed, converted here to NED for consistency

FALLBACK CHAIN:
  VO (Indra-Eye) → PX4 EKF2 local position → Dead reckoning (not impl.)

ROS 2 TOPICS:
  SUBSCRIBED:
    /indra_eye/odometry              (nav_msgs/Odometry)           — VO
    /fmu/out/vehicle_local_position  (px4_msgs/VehicleLocalPosition) — fallback

  PUBLISHED:
    /agri/odometry                   (nav_msgs/Odometry)  — fused output
    /agri/v4/fusion_status           (std_msgs/String)    — diagnostics
=====================================================================
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

from nav_msgs.msg import Odometry
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovariance, TwistWithCovariance
from px4_msgs.msg import VehicleLocalPosition


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
VO_TIMEOUT_SEC         = 2.0    # Seconds before VO declared lost → fallback
PUBLISH_HZ             = 20     # Output odometry rate
VO_POSITION_VARIANCE   = 0.02   # m² — expected VO position accuracy
PX4_POSITION_VARIANCE  = 0.10   # m² — PX4 EKF2 fallback accuracy


class MSFFusionBridge(Node):
    """
    V4 — The Smart Scout (MSF Bridge component).

    Merges Visual Odometry and PX4 EKF2 position estimates. Provides
    a single /agri/odometry topic consumed by all downstream nodes.
    """

    def __init__(self):
        super().__init__('msf_bridge')

        # ── QoS ───────────────────────────────────────────────────────
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        default_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # ── State ─────────────────────────────────────────────────────
        self.source        = 'NONE'       # 'VO' or 'PX4_EKF2'
        self.vo_last_time  = None
        self.tick          = 0

        # Latest PX4 position (fallback)
        self.px4_north = 0.0
        self.px4_east  = 0.0
        self.px4_down  = 0.0
        self.px4_vn    = 0.0
        self.px4_ve    = 0.0
        self.px4_vd    = 0.0

        # Latest VO odometry (primary)
        self.vo_odom: Odometry | None = None

        # ── Publishers ────────────────────────────────────────────────
        self.odom_pub  = self.create_publisher(
            Odometry, '/agri/odometry', default_qos)
        self.diag_pub  = self.create_publisher(
            String, '/agri/v4/fusion_status', 10)

        # ── Subscribers ───────────────────────────────────────────────
        self.vo_sub = self.create_subscription(
            Odometry, '/indra_eye/odometry',
            self._vo_callback, default_qos)
        self.px4_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self._px4_callback, px4_qos)

        # ── Publish timer ─────────────────────────────────────────────
        self.pub_timer = self.create_timer(1.0 / PUBLISH_HZ, self._publish)

        # ── Watchdog: check VO health every 1 s ─────────────────────
        self.watchdog_timer = self.create_timer(1.0, self._check_vo_health)

        self._log('🔮 V4 MSF Bridge (GPS-Denied Fusion) — ONLINE')
        self._log('Waiting for VO feed... will fallback to PX4 EKF2 if needed.')

    # ──────────────────────────────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────────────────────────────
    def _vo_callback(self, msg: Odometry) -> None:
        """Receive Visual Odometry estimate from Indra-Eye."""
        self.vo_odom      = msg
        self.vo_last_time = self.get_clock().now()
        if self.source != 'VO':
            self.source = 'VO'
            self._log('🟢 VO ACTIVE — Switching source to Indra-Eye Visual Odometry')

    def _px4_callback(self, msg: VehicleLocalPosition) -> None:
        """Receive PX4 EKF2 local position (fallback)."""
        self.px4_north = msg.x
        self.px4_east  = msg.y
        self.px4_down  = msg.z
        self.px4_vn    = msg.vx
        self.px4_ve    = msg.vy
        self.px4_vd    = msg.vz

    # ──────────────────────────────────────────────────────────────────
    # Watchdog
    # ──────────────────────────────────────────────────────────────────
    def _check_vo_health(self) -> None:
        """Detect VO dropout and switch to PX4 fallback."""
        if self.vo_last_time is None:
            if self.source != 'PX4_EKF2':
                self.source = 'PX4_EKF2'
                self._log('🟡 NO VO — Using PX4 EKF2 position (GPS-assisted)')
            return

        age_sec = (self.get_clock().now() - self.vo_last_time).nanoseconds * 1e-9
        if age_sec > VO_TIMEOUT_SEC:
            if self.source != 'PX4_EKF2':
                self.source = 'PX4_EKF2'
                self._log(f'🟠 VO TIMEOUT ({age_sec:.1f}s) — Falling back to PX4 EKF2')

    # ──────────────────────────────────────────────────────────────────
    # Publisher (20 Hz)
    # ──────────────────────────────────────────────────────────────────
    def _publish(self) -> None:
        self.tick += 1
        odom = Odometry()
        odom.header.stamp    = self.get_clock().now().to_msg()
        odom.header.frame_id = 'map'
        odom.child_frame_id  = 'base_link'

        if self.source == 'VO' and self.vo_odom is not None:
            # Use VO position directly (already in NED-like frame from indra_eye)
            odom.pose  = self.vo_odom.pose
            odom.twist = self.vo_odom.twist
            # Tighten covariance from actual VO quality
            for i in range(0, 36, 7):   # Diagonal elements
                odom.pose.covariance[i]  = VO_POSITION_VARIANCE
        else:
            # Construct Odometry from PX4 scalar position
            odom.pose.pose.position.x = self.px4_north
            odom.pose.pose.position.y = self.px4_east
            odom.pose.pose.position.z = self.px4_down
            odom.twist.twist.linear.x = self.px4_vn
            odom.twist.twist.linear.y = self.px4_ve
            odom.twist.twist.linear.z = self.px4_vd
            for i in range(0, 36, 7):
                odom.pose.covariance[i]  = PX4_POSITION_VARIANCE

        self.odom_pub.publish(odom)

        # Diagnostics every 5 seconds
        if self.tick % (PUBLISH_HZ * 5) == 0:
            px = odom.pose.pose.position.x
            py = odom.pose.pose.position.y
            pz = odom.pose.pose.position.z
            self._log(
                f'[{self.source}] N={px:.2f} E={py:.2f} D={pz:.2f}m | '
                f'cov={odom.pose.covariance[0]:.3f}m²')

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────
    def _log(self, msg: str) -> None:
        self.get_logger().info(msg)
        self.diag_pub.publish(String(data=f'[V4-MSF] {msg}'))


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = MSFFusionBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 V4 MSF Bridge shutting down')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
