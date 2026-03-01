#!/usr/bin/env python3
"""
path_planner.py — Layer 4 (V4): The Smart Scout — Path Planning
=====================================================================
PURPOSE (Kid Translation):
  "Before walking to the sick plant, the drone draws an invisible maze
  map in its head. It marks where the big trees and tractors are, then
  figures out the safest, fastest path to walk there without bumping
  its toes. It's like solving a puzzle before you move!"

TECHNICAL SUMMARY:
  Implements a self-contained A* (A-Star) path planner on a 2-D
  occupancy grid covering the bihar_maize Gazebo field.

  A* was chosen over RRT* in this implementation because:
    - Optimal path guaranteed on a discrete grid
    - Deterministic (reproducible results for experiments)
    - No external Nav2 dependency (works inside the Docker container)
    - Fast for moderate field sizes (40×40 = 1600 cells)

OCCUPANCY GRID:
  - Resolution: 0.5 m/cell
  - Coverage:   20 m × 20 m  →  40 × 40 cells
  - Obstacles:  Static AABBs extracted from bihar_maize.sdf
    (trees, boulders, tractor — hardcoded here, can be loaded from YAML)

ROS 2 TOPICS:
  SUBSCRIBED:
    /agri/navigate_to               (geometry_msgs/PoseStamped) — goal
    /fmu/out/vehicle_local_position (px4_msgs/VehicleLocalPosition) — start

  PUBLISHED:
    /agri/planned_path              (nav_msgs/Path)  — safe waypoints
    /agri/v4/status                 (std_msgs/String)

SELF-TEST:
  Run standalone (no ROS):
    python3 path_planner.py --selftest
  Prints an ASCII map with the computed path.
=====================================================================
"""

from __future__ import annotations   # PEP 563 — lazy evaluation of all annotations

import sys
import math
import heapq
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ROS 2 imports — guarded so that --selftest runs on host without rclpy.
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
    from geometry_msgs.msg import PoseStamped
    from nav_msgs.msg import Path
    from std_msgs.msg import String
    from px4_msgs.msg import VehicleLocalPosition
    _ROS_AVAILABLE = True
except ImportError:
    # Running in selftest mode on a host without ROS 2 installed.
    _ROS_AVAILABLE = False
    Node = object  # type: ignore[misc,assignment]


# ─────────────────────────────────────────────────────────────────────────────
# GRID CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
GRID_RESOLUTION_M  = 0.5    # Metres per grid cell
FIELD_WIDTH_M      = 20.0   # East extent
FIELD_HEIGHT_M     = 20.0   # North extent
GRID_COLS = int(FIELD_WIDTH_M  / GRID_RESOLUTION_M)   # 40
GRID_ROWS = int(FIELD_HEIGHT_M / GRID_RESOLUTION_M)   # 40

# Survey altitude for path execution (NED — negative = up)
PATH_ALTITUDE_NED = -5.0

# ─────────────────────────────────────────────────────────────────────────────
# STATIC OBSTACLES — AABB (bounding boxes) in world NED metres
# Format: (north_min, east_min, north_max, east_max)
# These are extracted from bihar_maize.sdf world file obstacles
# ─────────────────────────────────────────────────────────────────────────────
STATIC_OBSTACLES_AABB: List[Tuple[float, float, float, float]] = [
    (3.0,  7.0,  5.0,  9.0),    # Tree cluster 1
    (8.0,  2.0, 10.0,  4.0),    # Abandoned tractor
    (12.0, 14.0, 15.0, 16.0),   # Irrigation channel wall
    (17.0,  5.0, 19.0,  7.0),   # Tree cluster 2
    (6.0,  12.0,  8.0, 14.0),   # Storage shed corner
]
OBSTACLE_INFLATION_M = 1.0   # Safety margin around each obstacle


# ─────────────────────────────────────────────────────────────────────────────
# A* IMPLEMENTATION
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(order=True)
class _AStarNode:
    f: float
    g: float = field(compare=False)
    pos: Tuple[int, int] = field(compare=False)
    parent: Optional['_AStarNode'] = field(default=None, compare=False)


def _heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Octile distance heuristic — optimal for 8-connected grids."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def build_occupancy_grid(
    obstacles: List[Tuple[float, float, float, float]] = STATIC_OBSTACLES_AABB,
    inflation_m: float = OBSTACLE_INFLATION_M,
) -> List[List[int]]:
    """
    Build a 2-D occupancy grid.
    0 = free, 1 = occupied.
    Row index = North cell, Col index = East cell.
    """
    grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
    infl_cells = int(inflation_m / GRID_RESOLUTION_M)

    for (n_min, e_min, n_max, e_max) in obstacles:
        r_min = max(0, int(n_min / GRID_RESOLUTION_M) - infl_cells)
        r_max = min(GRID_ROWS - 1, int(n_max / GRID_RESOLUTION_M) + infl_cells)
        c_min = max(0, int(e_min / GRID_RESOLUTION_M) - infl_cells)
        c_max = min(GRID_COLS - 1, int(e_max / GRID_RESOLUTION_M) + infl_cells)
        for r in range(r_min, r_max + 1):
            for c in range(c_min, c_max + 1):
                grid[r][c] = 1

    return grid


def astar(
    grid: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Optional[List[Tuple[int, int]]]:
    """
    A* search on an 8-connected grid.

    Returns list of (row, col) cells from start to goal (inclusive),
    or None if no path exists.

    Kid Translation: "Like solving a maze — we try every direction from
    where we stand. We always pick the direction that looks closest to
    the exit AND has travelled the fewest steps so far. We mark visited
    spots with chalk so we don't go in circles."
    """
    rows, cols = len(grid), len(grid[0])
    DIRECTIONS = [
        (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),   # Cardinal
        (-1,-1, math.sqrt(2)), (-1, 1, math.sqrt(2)),             # Diagonal
        ( 1,-1, math.sqrt(2)), ( 1, 1, math.sqrt(2)),
    ]

    open_heap: list = []
    h0 = _heuristic(start, goal)
    start_node = _AStarNode(f=h0, g=0.0, pos=start)
    heapq.heappush(open_heap, start_node)

    g_map   = {start: 0.0}
    visited = set()

    while open_heap:
        current = heapq.heappop(open_heap)
        if current.pos in visited:
            continue
        visited.add(current.pos)

        if current.pos == goal:
            # Reconstruct path
            path = []
            node = current
            while node is not None:
                path.append(node.pos)
                node = node.parent
            return list(reversed(path))

        r, c = current.pos
        for dr, dc, cost in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if grid[nr][nc] == 1:
                continue
            nb_pos = (nr, nc)
            new_g  = current.g + cost
            if new_g < g_map.get(nb_pos, float('inf')):
                g_map[nb_pos] = new_g
                h = _heuristic(nb_pos, goal)
                nb_node = _AStarNode(f=new_g + h, g=new_g,
                                     pos=nb_pos, parent=current)
                heapq.heappush(open_heap, nb_node)

    return None   # No path found


def grid_to_world(
    cell: Tuple[int, int]
) -> Tuple[float, float]:
    """Convert grid (row, col) → world NED (north_m, east_m)."""
    north = (cell[0] + 0.5) * GRID_RESOLUTION_M
    east  = (cell[1] + 0.5) * GRID_RESOLUTION_M
    return north, east


def world_to_grid(
    north: float, east: float
) -> Tuple[int, int]:
    """Convert world NED (north_m, east_m) → grid (row, col), clamped."""
    row = int(max(0, min(GRID_ROWS - 1, north / GRID_RESOLUTION_M)))
    col = int(max(0, min(GRID_COLS - 1, east  / GRID_RESOLUTION_M)))
    return row, col


# ─────────────────────────────────────────────────────────────────────────────
# SELF-TEST (no ROS required)
# ─────────────────────────────────────────────────────────────────────────────
def _selftest() -> None:
    print('=== A* Path Planner Self-Test ===')
    grid = build_occupancy_grid()

    # Test: Start at (0, 0), Goal at (18, 18) — crosses multiple obstacles
    start_world = (0.5, 0.5)
    goal_world  = (18.5, 18.5)
    start_cell = world_to_grid(*start_world)
    goal_cell  = world_to_grid(*goal_world)

    print(f'Start (world): N={start_world[0]}m E={start_world[1]}m → cell {start_cell}')
    print(f'Goal  (world): N={goal_world[0]}m E={goal_world[1]}m → cell {goal_cell}')

    path = astar(grid, start_cell, goal_cell)

    if path is None:
        print('❌ FAIL: No path found!')
        sys.exit(1)

    print(f'✅ Path found: {len(path)} cells')

    # ASCII visualisation
    vis = [['.' if grid[r][c] == 0 else '█' for c in range(GRID_COLS)]
           for r in range(GRID_ROWS)]
    for cell in path:
        vis[cell[0]][cell[1]] = '·'
    vis[start_cell[0]][start_cell[1]] = 'S'
    vis[goal_cell[0]][goal_cell[1]]   = 'G'

    print('\nOccupancy grid (S=start, G=goal, █=obstacle, ·=path):')
    print('  ' + ''.join(str(c % 10) for c in range(GRID_COLS)))
    for r in range(GRID_ROWS - 1, -1, -1):  # Print North=top
        print(f'{r:2d}' + ''.join(vis[r]))

    path_len_m = (len(path) - 1) * GRID_RESOLUTION_M
    print(f'\nPath metrics: {len(path)} cells | {path_len_m:.1f} m total distance')
    print('=== Self-Test PASSED ✅ ===')


# ─────────────────────────────────────────────────────────────────────────────
# ROS 2 NODE
# ─────────────────────────────────────────────────────────────────────────────
class PathPlannerNode(Node):
    """
    V4 — The Smart Scout (Path Planning component).

    Listens for navigation goals, computes an A* path avoiding known
    obstacles in the bihar_maize world, and publishes the waypoint
    sequence as a nav_msgs/Path for the sprayer / mission commander.
    """

    def __init__(self):
        super().__init__('path_planner')

        # ── QoS ───────────────────────────────────────────────────────
        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # ── Build occupancy grid once at startup ──────────────────────
        self.grid = build_occupancy_grid()
        self.get_logger().info(
            f'🗺️  Occupancy grid built: {GRID_ROWS}×{GRID_COLS} cells '
            f'({FIELD_HEIGHT_M}m × {FIELD_WIDTH_M}m @ '
            f'{GRID_RESOLUTION_M}m/cell) | '
            f'{len(STATIC_OBSTACLES_AABB)} obstacle regions loaded')

        # ── State ─────────────────────────────────────────────────────
        self.drone_north = 0.0
        self.drone_east  = 0.0

        # ── Publishers ────────────────────────────────────────────────
        self.path_pub   = self.create_publisher(Path,   '/agri/planned_path', 10)
        self.status_pub = self.create_publisher(String, '/agri/v4/status', 10)

        # ── Subscribers ───────────────────────────────────────────────
        self.goal_sub = self.create_subscription(
            PoseStamped, '/agri/navigate_to',
            self._goal_callback, 10)
        self.pos_sub = self.create_subscription(
            VehicleLocalPosition, '/fmu/out/vehicle_local_position',
            self._pos_callback, px4_qos)

        self._log('🧭 V4 Path Planner (A*) — ONLINE')
        self._log(f'Listening on /agri/navigate_to for goal requests')

    # ──────────────────────────────────────────────────────────────────
    # Callbacks
    # ──────────────────────────────────────────────────────────────────
    def _pos_callback(self, msg: VehicleLocalPosition) -> None:
        self.drone_north = msg.x
        self.drone_east  = msg.y

    def _goal_callback(self, goal_msg: PoseStamped) -> None:
        """Triggered when a navigation goal arrives. Run A* and publish path."""
        goal_n = goal_msg.pose.position.x
        goal_e = goal_msg.pose.position.y

        self._log(f'📍 New goal received: N={goal_n:.2f} E={goal_e:.2f}')

        start_cell = world_to_grid(self.drone_north, self.drone_east)
        goal_cell  = world_to_grid(goal_n, goal_e)

        if self.grid[goal_cell[0]][goal_cell[1]] == 1:
            self._log(f'⚠️  Goal cell {goal_cell} is OCCUPIED — '
                      'finding nearest free cell...')
            goal_cell = self._nearest_free(goal_cell)
            if goal_cell is None:
                self._log('❌ No reachable free cell near goal. Aborting.')
                return

        path_cells = astar(self.grid, start_cell, goal_cell)

        if path_cells is None:
            self._log(f'❌ A* found NO path from {start_cell} → {goal_cell}')
            return

        path_len_m = (len(path_cells) - 1) * GRID_RESOLUTION_M
        self._log(f'✅ A* path found: {len(path_cells)} waypoints | '
                  f'{path_len_m:.1f} m total distance')

        # Publish nav_msgs/Path
        ros_path = Path()
        ros_path.header.stamp    = self.get_clock().now().to_msg()
        ros_path.header.frame_id = 'map'

        for cell in path_cells:
            n, e = grid_to_world(cell)
            pose = PoseStamped()
            pose.header = ros_path.header
            pose.pose.position.x = n                   # North
            pose.pose.position.y = e                   # East
            pose.pose.position.z = PATH_ALTITUDE_NED   # NED altitude
            ros_path.poses.append(pose)

        self.path_pub.publish(ros_path)
        self._log(f'📡 Published planned path ({len(path_cells)} poses) '
                  f'on /agri/planned_path')

    # ──────────────────────────────────────────────────────────────────
    # Utilities
    # ──────────────────────────────────────────────────────────────────
    def _nearest_free(self, cell: Tuple[int, int],
                      search_r: int = 3) -> Optional[Tuple[int, int]]:
        """BFS to find nearest unoccupied cell."""
        from collections import deque
        q = deque([cell])
        visited = {cell}
        while q:
            r, c = q.popleft()
            if self.grid[r][c] == 0:
                return (r, c)
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if (0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS
                        and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    q.append((nr, nc))
        return None

    def _log(self, msg: str) -> None:
        self.get_logger().info(msg)
        self.status_pub.publish(String(data=f'[V4-Planner] {msg}'))


# ─────────────────────────────────────────────────────────────────────────────
def main(args=None):
    # ── Handle --selftest WITHOUT needing ROS ───────────────────────────────
    if '--selftest' in (args or sys.argv):
        _selftest()
        return

    if not _ROS_AVAILABLE:
        print('ERROR: rclpy not found. Run inside Docker or use --selftest.')
        sys.exit(1)

    rclpy.init(args=args)
    node = PathPlannerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('🛑 V4 Path Planner shutting down')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
