#!/usr/bin/env python3
"""
agri_sprayer_control.py — Layer 3 (V3): The Helper
=====================================================================
PURPOSE (Kid Translation):
  "The drone carries a tiny water bottle. When the Doctor (V2) sends a
  note saying 'Plant #7 has fever, it lives at X=12, Y=8', this node
  reads the note, flies to that exact spot, hovers, and goes PSSST —
  giving the sick plant its medicine. Then it waits for the next note."

TECHNICAL SUMMARY:
  - Subscribes to /agri/plant_health/status (PlantHealthStatus)
  - Queues incoming anomaly targets for treatment
  - Navigates to each target using PX4 TrajectorySetpoint (NED offboard)
  - On arrival (< 0.5 m), triggers sprayer for spray_duration_sec seconds
  - Publishes SprayCommand status updates
  - Logs every spray event to /reports/spray_log.csv for post-mission audit

ROS 2 TOPICS:
  SUBSCRIBED:
    /agri/plant_health/status        (agri_msgs/PlantHealthStatus)
    /fmu/out/vehicle_local_position  (px4_msgs/VehicleLocalPosition)

  PUBLISHED:
    /fmu/in/offboard_control_mode    (px4_msgs/OffboardControlMode)
    /fmu/in/trajectory_setpoint      (px4_msgs/TrajectorySetpoint)
    /fmu/in/vehicle_command          (px4_msgs/VehicleCommand)
    /agri/sprayer_active             (std_msgs/Bool)
    /agri/spray_command              (agri_msgs/SprayCommand)
    /agri/v3/status                  (std_msgs/String)   — mission log
=====================================================================
"""

import csv
import math
import os
from collections import deque

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

from std_msgs.msg import Bool, String
from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
)
from agri_msgs.msg import PlantHealthStatus, SprayCommand


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SPRAY_ALTITUDE_NED  = -2.5      # NED: drop from survey alt to spraying alt
ARRIVAL_TOLERANCE_M = 0.5       # Metres: "close enough" to trigger spray
SPRAY_DOSE_ML       = 5.0       # Simulated dose per plant
SPRAY_DURATION_SEC  = 2.0       # Valve open time
SPRAY_LOG_PATH      = '/reports/spray_log.csv'
LOOP_HZ             = 10        # Control loop frequency


# ─────────────────────────────────────────────────────────────────────────────
# NODE
# ─────────────────────────────────────────────────────────────────────────────
class AgriSprayerControl(Node):
    """
    V3 — The Helper: Targeted precision sprayer controller.

    State machine (per target):
        IDLE → NAVIGATING → DESCENDING → SPRAYING → ASCENDING → IDLE
    """

    def __init__(self):
        super().__init__('agri_sprayer_control')

        # ── QoS ───────────────────────────────────────────────────────
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # ── State ─────────────────────────────────────────────────────
        self.state          = 'IDLE'
        self.tick           = 0
        self.spray_tick     = 0
        self.current_target : PlantHealthStatus | None = None
        self.target_queue   : deque = deque()

        self.drone_x = 0.0    # North
        self.drone_y = 0.0    # East
        self.drone_z = 0.0    # NED Down (negative = up)
        self.return_z = -5.0  # Altitude to return to after spray

        self.sprays_completed = 0

        # ── Publishers ────────────────────────────────────────────────
        self.offboard_pub  = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', px4_qos)
        self.traj_pub      = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', px4_qos)
        self.cmd_pub       = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', px4_qos)
        self.sprayer_pub   = self.create_publisher(
            Bool, '/agri/sprayer_active', 10)
        self.spray_cmd_pub = self.create_publisher(
            SprayCommand, '/agri/spray_command', 10)
        self.status_pub    = self.create_publisher(
            String, '/agri/v3/status', 10)

        # ── Subscribers ───────────────────────────────────────────────
        self.health_sub = self.create_subscription(
            PlantHealthStatus, '/agri/plant_health/status',
            self._health_callback, 10)
        self.pos_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self._pos_callback, px4_qos)

        # ── CSV log ───────────────────────────────────────────────────
        os.makedirs('/reports', exist_ok=True)
        self._init_csv()

        # ── Timer ─────────────────────────────────────────────────────
        self.timer = self.create_timer(1.0 / LOOP_HZ, self._tick)

        self._log('💊 V3 Sprayer Control (The Helper) — ONLINE')
        self._log(f'Dose: {SPRAY_DOSE_ML} ml | '
                  f'Duration: {SPRAY_DURATION_SEC} s | '
                  f'Arrival tolerance: {ARRIVAL_TOLERANCE_M} m')

    # ──────────────────────────────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────────────────────────────
    def _pos_callback(self, msg: VehicleLocalPosition) -> None:
        self.drone_x = msg.x
        self.drone_y = msg.y
        self.drone_z = msg.z

    def _health_callback(self, msg: PlantHealthStatus) -> None:
        """Queue new plant anomaly targets as they arrive from V2."""
        # Avoid duplicate plant IDs in queue
        existing_ids = {t.plant_id for t in self.target_queue}
        if (self.current_target and msg.plant_id == self.current_target.plant_id):
            return
        if msg.plant_id in existing_ids:
            return

        self.target_queue.append(msg)
        self._log(f'📋 Queued Plant#{msg.plant_id} at '
                  f'N={msg.world_x:.2f} E={msg.world_y:.2f} '
                  f'[{msg.description.split("|")[0].strip()}]')

    # ──────────────────────────────────────────────────────────────────
    # 10 Hz control loop
    # ──────────────────────────────────────────────────────────────────
    def _tick(self) -> None:
        self.tick += 1
        self._publish_offboard_keepalive()

        if self.state == 'IDLE':
            if self.target_queue:
                self.current_target = self.target_queue.popleft()
                self.return_z = self.drone_z    # Remember current altitude
                self.state = 'NAVIGATING'
                self._log(
                    f'🚁 Navigating to Plant#{self.current_target.plant_id} | '
                    f'N={self.current_target.world_x:.2f} '
                    f'E={self.current_target.world_y:.2f}')
                self._publish_spray_cmd(SprayCommand.STATUS_NAVIGATING)

        elif self.state == 'NAVIGATING':
            # Fly to target XY at survey altitude
            self._goto(self.current_target.world_x,
                       self.current_target.world_y,
                       self.return_z)
            if self._at_xy(self.current_target.world_x,
                           self.current_target.world_y):
                self.state = 'DESCENDING'
                self._log(f'📍 Arrived at Plant#{self.current_target.plant_id}. '
                          'Descending to spray altitude...')

        elif self.state == 'DESCENDING':
            self._goto(self.current_target.world_x,
                       self.current_target.world_y,
                       SPRAY_ALTITUDE_NED)
            if abs(self.drone_z - SPRAY_ALTITUDE_NED) < 0.4:
                self.state = 'SPRAYING'
                self.spray_tick = 0
                self._activate_sprayer(True)
                self._publish_spray_cmd(SprayCommand.STATUS_SPRAYING)
                self._log(f'💦 SPRAYING Plant#{self.current_target.plant_id} '
                          f'— {SPRAY_DOSE_ML} ml for {SPRAY_DURATION_SEC} s')

        elif self.state == 'SPRAYING':
            # Hold position while spraying
            self._goto(self.current_target.world_x,
                       self.current_target.world_y,
                       SPRAY_ALTITUDE_NED)
            self.spray_tick += 1
            if self.spray_tick >= int(SPRAY_DURATION_SEC * LOOP_HZ):
                self._activate_sprayer(False)
                self.state = 'ASCENDING'
                self.sprays_completed += 1
                self._log_to_csv(self.current_target)
                self._publish_spray_cmd(SprayCommand.STATUS_COMPLETE)
                self._log(f'✅ Spray COMPLETE for Plant#{self.current_target.plant_id} '
                          f'| Total sprays: {self.sprays_completed}')

        elif self.state == 'ASCENDING':
            # Return to survey altitude
            self._goto(self.current_target.world_x,
                       self.current_target.world_y,
                       self.return_z)
            if abs(self.drone_z - self.return_z) < 0.5:
                self.state = 'IDLE'
                self.current_target = None
                self._log('🔄 Spray cycle done. Returning to IDLE for next target.')

    # ──────────────────────────────────────────────────────────────────
    # PX4 Helpers
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

    def _goto(self, north: float, east: float, down: float) -> None:
        msg = TrajectorySetpoint()
        msg.position  = [north, east, down]
        msg.yaw       = 0.0
        msg.timestamp = self._now()
        self.traj_pub.publish(msg)

    def _at_xy(self, target_n: float, target_e: float) -> bool:
        dist = math.sqrt((self.drone_x - target_n) ** 2 +
                         (self.drone_y - target_e) ** 2)
        return dist < ARRIVAL_TOLERANCE_M

    def _activate_sprayer(self, active: bool) -> None:
        msg = Bool()
        msg.data = active
        self.sprayer_pub.publish(msg)

    def _publish_spray_cmd(self, status: int) -> None:
        if self.current_target is None:
            return
        msg = SprayCommand()
        msg.header.stamp    = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        msg.plant_id        = self.current_target.plant_id
        msg.target_x        = self.current_target.world_x
        msg.target_y        = self.current_target.world_y
        msg.target_z        = SPRAY_ALTITUDE_NED
        msg.dose_ml         = SPRAY_DOSE_ML
        msg.spray_duration_sec = SPRAY_DURATION_SEC
        msg.status          = status
        self.spray_cmd_pub.publish(msg)

    # ──────────────────────────────────────────────────────────────────
    # CSV Logging
    # ──────────────────────────────────────────────────────────────────
    def _init_csv(self) -> None:
        if not os.path.exists(SPRAY_LOG_PATH):
            with open(SPRAY_LOG_PATH, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp_ns', 'plant_id', 'severity',
                    'world_north_m', 'world_east_m', 'spray_altitude_ned',
                    'dose_ml', 'duration_sec', 'confidence',
                ])

    def _log_to_csv(self, target: PlantHealthStatus) -> None:
        ts = self.get_clock().now().nanoseconds
        with open(SPRAY_LOG_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                ts, target.plant_id, target.severity,
                f'{target.world_x:.3f}', f'{target.world_y:.3f}',
                SPRAY_ALTITUDE_NED, SPRAY_DOSE_ML, SPRAY_DURATION_SEC,
                f'{target.confidence:.3f}',
            ])

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────
    def _log(self, msg: str) -> None:
        self.get_logger().info(msg)
        self.status_pub.publish(String(data=f'[V3] {msg}'))

    def _now(self) -> int:
        return int(self.get_clock().now().nanoseconds / 1000)


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = AgriSprayerControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 V3 Sprayer Control shutting down')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
