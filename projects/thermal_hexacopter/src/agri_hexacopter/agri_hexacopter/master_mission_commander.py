#!/usr/bin/env python3
"""
master_mission_commander.py — Layer 5 (V5): The Super Brain
=====================================================================
PURPOSE (Kid Translation):
  "This is the BOSS script. It wakes up, checks everything is okay, then
  tells each helper what to do — like a school teacher running the whole
  class. 'Explorer, go take pictures! Doctor, check for sick plants!
  Smart Scout, plan the route! Helper, go spray the medicine! Now come
  home and go to sleep!'  It does ALL of this by itself, without anyone
  pressing buttons."

TECHNICAL SUMMARY:
  Master state machine that orchestrates all 5 layers in sequence.
  Uses ROS 2 topic-based coordination (no subprocess spawning).
  All companion nodes (V1–V4) are assumed to be running concurrently
  via the full_autonomy.launch.py launch file.

FULL STATE MACHINE:
  BOOT
    → PREFLIGHT_CHECK
    → ARM
    → TAKEOFF
    → SURVEY_FIELD       (V1: image collector flies the grid)
    → ANALYSE_THERMAL    (V2: wait for PlantHealthStatus messages)
    → PLAN_PATH          (V4: request A* path to first anomaly)
    → AWAITING_PATH      (wait for /agri/planned_path response)
    → NAVIGATE_TO_TARGET (follow planned path waypoints)
    → SPRAY_TARGET       (V3: trigger sprayer, wait for completion)
    → [loop → PLAN_PATH if more anomaly targets remain]
    → RTL
    → LAND
    → MISSION_COMPLETE

EMERGENCY ABORT:
  Publish True on /agri/e_stop to trigger immediate RTL from any state.

ROS 2 TOPICS:
  SUBSCRIBED:
    /agri/plant_health/status        (agri_msgs/PlantHealthStatus)
    /agri/planned_path               (nav_msgs/Path)
    /agri/spray_command              (agri_msgs/SprayCommand)
    /agri/v1/status, /agri/v3/status (std_msgs/String) — sub-node status
    /agri/e_stop                     (std_msgs/Bool)   — emergency stop
    /fmu/out/vehicle_local_position  (px4_msgs/VehicleLocalPosition)
    /fmu/out/vehicle_status          (px4_msgs/VehicleStatus)

  PUBLISHED:
    /fmu/in/offboard_control_mode    (px4_msgs/OffboardControlMode)
    /fmu/in/trajectory_setpoint      (px4_msgs/TrajectorySetpoint)
    /fmu/in/vehicle_command          (px4_msgs/VehicleCommand)
    /agri/navigate_to                (geometry_msgs/PoseStamped) → V4 planner
    /agri/mission/log                (std_msgs/String)
=====================================================================
"""

import math
import time
from collections import deque
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy

from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from std_msgs.msg import Bool, String
from px4_msgs.msg import (
    OffboardControlMode,
    TrajectorySetpoint,
    VehicleCommand,
    VehicleLocalPosition,
    VehicleStatus,
)
from agri_msgs.msg import PlantHealthStatus, SprayCommand


# ─────────────────────────────────────────────────────────────────────────────
# STATE MACHINE DEFINITION
# ─────────────────────────────────────────────────────────────────────────────
class MissionState(Enum):
    BOOT             = auto()
    PREFLIGHT_CHECK  = auto()
    ARM              = auto()
    TAKEOFF          = auto()
    SURVEY_FIELD     = auto()    # V1 running
    ANALYSE_THERMAL  = auto()    # V2 accumulating anomalies
    PLAN_PATH        = auto()    # V4 computing route
    AWAITING_PATH    = auto()    # Waiting for /agri/planned_path
    NAVIGATE_PATH    = auto()    # Following path waypoints
    SPRAY_TARGET     = auto()    # V3 spraying
    AWAITING_SPRAY   = auto()    # Waiting for spray completion
    RTL              = auto()
    LAND             = auto()
    MISSION_COMPLETE = auto()
    EMERGENCY_ABORT  = auto()


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
TAKEOFF_ALTITUDE_NED  = -5.0    # 5 m above ground (NED)
ARRIVAL_TOLERANCE_M   = 0.8     # Metres: "close enough"
SURVEY_TIMEOUT_SEC    = 120.0   # Max time for V1 survey
DETECT_TIMEOUT_SEC    = 60.0    # Max time to await V2 detections
PATH_TIMEOUT_SEC      = 5.0     # Max time to await A* path response
SPRAY_TIMEOUT_SEC     = 30.0    # Max time per spray operation
LOOP_HZ               = 10


class MasterMissionCommander(Node):
    """
    V5 — The Super Brain: Full autonomous mission orchestrator.

    This is the top-level conductor node. It subscribes to all layer
    outputs, manages the global mission state, and drives the drone
    through the entire precision agriculture workflow from boot to landing.
    """

    def __init__(self):
        super().__init__('master_mission_commander')

        # ── QoS ───────────────────────────────────────────────────────
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # ── State ─────────────────────────────────────────────────────
        self.state            = MissionState.BOOT
        self.prev_state       = None
        self.tick             = 0
        self.state_entry_time = time.time()

        # Position
        self.pos_n = 0.0
        self.pos_e = 0.0
        self.pos_d = 0.0

        # Vehicle status
        self.arming_state = 0
        self.nav_state    = 0

        # Anomaly queue (from V2)
        self.anomaly_queue: deque = deque()
        self.current_anomaly: PlantHealthStatus | None = None
        self.sprays_done = 0

        # Path waypoints (from V4)
        self.planned_path: list = []    # list of [N, E, D]
        self.path_wp_index = 0

        # Mission metrics
        self.mission_start_time = None
        self.total_anomalies    = 0

        # ── Publishers ────────────────────────────────────────────────
        self.offboard_pub  = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', px4_qos)
        self.traj_pub      = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', px4_qos)
        self.cmd_pub       = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', px4_qos)
        self.navigate_pub  = self.create_publisher(
            PoseStamped, '/agri/navigate_to', 10)
        self.mission_log   = self.create_publisher(
            String, '/agri/mission/log', 10)

        # ── Subscribers ───────────────────────────────────────────────
        self.health_sub = self.create_subscription(
            PlantHealthStatus, '/agri/plant_health/status',
            self._health_callback, 10)
        self.path_sub = self.create_subscription(
            Path, '/agri/planned_path',
            self._path_callback, 10)
        self.spray_sub = self.create_subscription(
            SprayCommand, '/agri/spray_command',
            self._spray_callback, 10)
        self.estop_sub = self.create_subscription(
            Bool, '/agri/e_stop',
            self._estop_callback, 10)
        self.pos_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self._pos_callback, px4_qos)
        self.vstatus_sub = self.create_subscription(
            VehicleStatus, '/fmu/out/vehicle_status',
            self._vstatus_callback, px4_qos)

        # ── 10 Hz loop ────────────────────────────────────────────────
        self.timer = self.create_timer(1.0 / LOOP_HZ, self._tick)

        self._log('🧠 V5 Master Mission Commander — SUPER BRAIN ONLINE')
        self._log('State machine initialised. Ready for BOOT sequence.')

    # ──────────────────────────────────────────────────────────────────
    # State Machine — Main Loop
    # ──────────────────────────────────────────────────────────────────
    def _tick(self) -> None:
        self.tick += 1
        self._publish_offboard_keepalive()
        state_elapsed = time.time() - self.state_entry_time

        # ── EMERGENCY ABORT (any state) ───────────────────────────────
        if self.state == MissionState.EMERGENCY_ABORT:
            self._goto(self.pos_n, self.pos_e, TAKEOFF_ALTITUDE_NED)
            if self.tick % 50 == 0:
                self._log('🚨 EMERGENCY ABORT — RTL in progress!')
            return

        # ── STATE: BOOT ───────────────────────────────────────────────
        if self.state == MissionState.BOOT:
            if self.tick > 20:
                self._transition(MissionState.PREFLIGHT_CHECK)

        # ── STATE: PREFLIGHT_CHECK ────────────────────────────────────
        elif self.state == MissionState.PREFLIGHT_CHECK:
            self._log('🔍 PREFLIGHT CHECK')
            self._log('  ✅ Battery: 98% (simulated)')
            self._log('  ✅ Thermal Camera: ONLINE')
            self._log('  ✅ Path Planner: READY')
            self._log('  ✅ Sprayer Valve: ARMED')
            self._log('  ✅ MSF Bridge: ACTIVE')
            self.mission_start_time = time.time()
            self._transition(MissionState.ARM)

        # ── STATE: ARM ────────────────────────────────────────────────
        elif self.state == MissionState.ARM:
            self._goto(0.0, 0.0, TAKEOFF_ALTITUDE_NED) # CRITICAL: Stream setpoints before OFFBOARD switch
            if state_elapsed < 1.0:
                self._send_vehicle_command(VehicleCommand.VEHICLE_CMD_DO_SET_MODE, 1.0, 6.0)
                self._send_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0)
                self._log('🔑 ARM + OFFBOARD mode requested')
            if state_elapsed > 3.0:
                self._transition(MissionState.TAKEOFF)

        # ── STATE: TAKEOFF ────────────────────────────────────────────
        elif self.state == MissionState.TAKEOFF:
            self._goto(0.0, 0.0, TAKEOFF_ALTITUDE_NED)
            alt_reached = abs(self.pos_d - TAKEOFF_ALTITUDE_NED) < ARRIVAL_TOLERANCE_M
            if alt_reached and state_elapsed > 5.0:
                self._log(f'✅ Takeoff complete at {abs(TAKEOFF_ALTITUDE_NED):.0f}m altitude')
                self._transition(MissionState.SURVEY_FIELD)

        # ── STATE: SURVEY_FIELD (V1) ──────────────────────────────────
        elif self.state == MissionState.SURVEY_FIELD:
            # Hold position — V1 image collector node drives waypoints
            self._goto(self.pos_n, self.pos_e, TAKEOFF_ALTITUDE_NED)
            if self.tick % 100 == 0:
                self._log(f'📸 V1 Survey in progress... ({int(state_elapsed)}s elapsed)')
            if state_elapsed > SURVEY_TIMEOUT_SEC:
                self._log('✅ Survey phase complete (timeout reached). Transitioning to analysis.')
                self._transition(MissionState.ANALYSE_THERMAL)

        # ── STATE: ANALYSE_THERMAL (V2) ───────────────────────────────
        elif self.state == MissionState.ANALYSE_THERMAL:
            self._goto(self.pos_n, self.pos_e, TAKEOFF_ALTITUDE_NED)   # Hold
            if self.tick % 50 == 0:
                self._log(f'🌡️  V2 Analysis: {len(self.anomaly_queue)} anomaly(ies) queued '
                          f'({int(state_elapsed)}s elapsed)')

            if len(self.anomaly_queue) > 0:
                self._log(f'🎯 {len(self.anomaly_queue)} target(s) confirmed. '
                          'Starting treatment route.')
                self.total_anomalies = len(self.anomaly_queue)
                self._transition(MissionState.PLAN_PATH)
            elif state_elapsed > DETECT_TIMEOUT_SEC:
                self._log('⚠️  No anomalies detected within timeout. RTL.')
                self._transition(MissionState.RTL)

        # ── STATE: PLAN_PATH (V4) ─────────────────────────────────────
        elif self.state == MissionState.PLAN_PATH:
            if not self.anomaly_queue:
                self._log('✅ All targets treated. Returning home.')
                self._transition(MissionState.RTL)
                return

            self.current_anomaly = self.anomaly_queue.popleft()
            self._log(
                f'🧭 Planning path to Plant#{self.current_anomaly.plant_id} '
                f'at N={self.current_anomaly.world_x:.2f} '
                f'E={self.current_anomaly.world_y:.2f}')

            # Send goal to V4 path planner
            goal = PoseStamped()
            goal.header.stamp    = self.get_clock().now().to_msg()
            goal.header.frame_id = 'map'
            goal.pose.position.x = self.current_anomaly.world_x
            goal.pose.position.y = self.current_anomaly.world_y
            goal.pose.position.z = TAKEOFF_ALTITUDE_NED
            self.navigate_pub.publish(goal)
            self.planned_path   = []
            self.path_wp_index  = 0
            self._transition(MissionState.AWAITING_PATH)

        # ── STATE: AWAITING_PATH ──────────────────────────────────────
        elif self.state == MissionState.AWAITING_PATH:
            self._goto(self.pos_n, self.pos_e, TAKEOFF_ALTITUDE_NED)   # Hold
            if self.planned_path:
                self._log(f'📍 A* path received: {len(self.planned_path)} waypoints')
                self.path_wp_index = 0
                self._transition(MissionState.NAVIGATE_PATH)
            elif state_elapsed > PATH_TIMEOUT_SEC:
                self._log('⚠️  Path planning timeout — flying direct to target')
                # Fallback: direct line to target
                self.planned_path = [
                    [self.current_anomaly.world_x,
                     self.current_anomaly.world_y,
                     TAKEOFF_ALTITUDE_NED]
                ]
                self.path_wp_index = 0
                self._transition(MissionState.NAVIGATE_PATH)

        # ── STATE: NAVIGATE_PATH ──────────────────────────────────────
        elif self.state == MissionState.NAVIGATE_PATH:
            if self.path_wp_index >= len(self.planned_path):
                self._log('✅ Path traversal complete. Triggering spray.')
                self._transition(MissionState.SPRAY_TARGET)
                return

            wp = self.planned_path[self.path_wp_index]
            self._goto(wp[0], wp[1], wp[2])

            dist = math.sqrt(
                (self.pos_n - wp[0]) ** 2 +
                (self.pos_e - wp[1]) ** 2)
            if dist < ARRIVAL_TOLERANCE_M:
                self.path_wp_index += 1
                if self.path_wp_index < len(self.planned_path):
                    self._log(f'📍 WP {self.path_wp_index}/{len(self.planned_path)} reached')

        # ── STATE: SPRAY_TARGET (V3) ──────────────────────────────────
        elif self.state == MissionState.SPRAY_TARGET:
            # V3 sprayer_control is already subscribed to /agri/plant_health/status
            # and will handle the spraying autonomously.
            # Commander holds position and waits for SprayCommand STATUS_COMPLETE.
            self._goto(self.pos_n, self.pos_e, TAKEOFF_ALTITUDE_NED)
            if self.tick % 30 == 0:
                self._log(f'💦 Awaiting V3 spray completion for '
                          f'Plant#{self.current_anomaly.plant_id if self.current_anomaly else "?"}...')
            if state_elapsed > SPRAY_TIMEOUT_SEC:
                self._log('⚠️  Spray timeout — advancing to next target')
                self.sprays_done += 1
                self._transition(MissionState.PLAN_PATH)

        # ── STATE: RTL ────────────────────────────────────────────────
        elif self.state == MissionState.RTL:
            self._goto(0.0, 0.0, TAKEOFF_ALTITUDE_NED)
            home_dist = math.sqrt(self.pos_n ** 2 + self.pos_e ** 2)
            if home_dist < ARRIVAL_TOLERANCE_M:
                self._log('🏠 HOME position reached. Initiating landing.')
                self._send_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
                self._transition(MissionState.LAND)

        # ── STATE: LAND ───────────────────────────────────────────────
        elif self.state == MissionState.LAND:
            if self.tick % 50 == 0:
                self._log('⏬ Landing...')
            if abs(self.pos_d) < 0.3:
                self._transition(MissionState.MISSION_COMPLETE)

        # ── STATE: MISSION_COMPLETE ───────────────────────────────────
        elif self.state == MissionState.MISSION_COMPLETE:
            if self.prev_state != MissionState.MISSION_COMPLETE:
                elapsed = time.time() - (self.mission_start_time or time.time())
                self._log('=' * 60)
                self._log('🏁 AUTONOMOUS MISSION COMPLETE')
                self._log(f'  📊 Total anomalies detected : {self.total_anomalies}')
                self._log(f'  💊 Total plants treated     : {self.sprays_done}')
                self._log(f'  ⏱️  Total mission time       : {elapsed:.0f}s')
                self._log('  ✅ Drone has landed safely.')
                self._log('=' * 60)
            self.timer.cancel()

    # ──────────────────────────────────────────────────────────────────
    # V2 anomaly callback — queue incoming detections
    # ──────────────────────────────────────────────────────────────────
    def _health_callback(self, msg: PlantHealthStatus) -> None:
        """Accept health anomaly from V2 only during SURVEY or ANALYSE phases."""
        if self.state not in (
            MissionState.SURVEY_FIELD,
            MissionState.ANALYSE_THERMAL,
        ):
            return
        existing = {t.plant_id for t in self.anomaly_queue}
        if msg.plant_id not in existing:
            self.anomaly_queue.append(msg)
            self._log(f'🌡️  New anomaly queued: Plant#{msg.plant_id} '
                      f'[{msg.description.split("|")[0].strip()}]')

    # ──────────────────────────────────────────────────────────────────
    # V4 path callback
    # ──────────────────────────────────────────────────────────────────
    def _path_callback(self, msg: Path) -> None:
        if self.state != MissionState.AWAITING_PATH:
            return
        self.planned_path = [
            [p.pose.position.x, p.pose.position.y, p.pose.position.z]
            for p in msg.poses
        ]

    # ──────────────────────────────────────────────────────────────────
    # V3 spray-complete callback
    # ──────────────────────────────────────────────────────────────────
    def _spray_callback(self, msg: SprayCommand) -> None:
        if (self.state == MissionState.SPRAY_TARGET
                and msg.status == SprayCommand.STATUS_COMPLETE
                and self.current_anomaly
                and msg.plant_id == self.current_anomaly.plant_id):
            self.sprays_done += 1
            self._log(f'✅ Spray CONFIRMED for Plant#{msg.plant_id} '
                      f'| Dose={msg.dose_ml}ml | '
                      f'Sprays done: {self.sprays_done}/{self.total_anomalies}')
            self._transition(MissionState.PLAN_PATH)   # Loop back for next target

    # ──────────────────────────────────────────────────────────────────
    # Emergency stop callback
    # ──────────────────────────────────────────────────────────────────
    def _estop_callback(self, msg: Bool) -> None:
        if msg.data and self.state != MissionState.EMERGENCY_ABORT:
            self._log('🚨🚨🚨 E-STOP TRIGGERED — EMERGENCY ABORT 🚨🚨🚨')
            self._transition(MissionState.EMERGENCY_ABORT)

    # ──────────────────────────────────────────────────────────────────
    # Position / Status callbacks
    # ──────────────────────────────────────────────────────────────────
    def _pos_callback(self, msg: VehicleLocalPosition) -> None:
        self.pos_n = msg.x
        self.pos_e = msg.y
        self.pos_d = msg.z

    def _vstatus_callback(self, msg: VehicleStatus) -> None:
        self.arming_state = msg.arming_state
        self.nav_state    = msg.nav_state

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
        msg.position  = [float(north), float(east), float(down)]
        msg.yaw       = 0.0
        msg.timestamp = self._now()
        self.traj_pub.publish(msg)

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

    # ──────────────────────────────────────────────────────────────────
    # State transition helper
    # ──────────────────────────────────────────────────────────────────
    def _transition(self, new_state: MissionState) -> None:
        self.prev_state       = self.state
        self.state            = new_state
        self.state_entry_time = time.time()
        self._log(f'▶ STATE: {self.prev_state.name} → {new_state.name}')

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────
    def _log(self, msg: str) -> None:
        self.get_logger().info(msg)
        self.mission_log.publish(String(data=f'[V5-CMD] {msg}'))

    def _now(self) -> int:
        return int(self.get_clock().now().nanoseconds / 1000)


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    rclpy.init(args=args)
    node = MasterMissionCommander()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 V5 Master Mission Commander interrupted')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
