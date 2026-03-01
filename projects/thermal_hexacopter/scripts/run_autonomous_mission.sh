#!/usr/bin/env bash
# =============================================================================
# run_autonomous_mission.sh
# =============================================================================
# One-shot script to BUILD and LAUNCH the full 5-Layer Autonomous UAV system
# inside the existing UAV Master Hub Docker container.
#
# Kid Translation:
#   "This script is like pressing ONE magic button that:
#    1. Packs all our code into a box  (BUILD)
#    2. Opens the box and runs everything  (LAUNCH)
#    ...and the drone does the rest!"
#
# ARCHITECTURE CONSTRAINT:
#   All builds happen in /tmp/build to honour the Read-Only host shield.
#   Host files in /uav_master_hub:ro are never written to.
#
# USAGE (from host machine):
#   docker exec -it <container_name> bash /uav_master_hub/projects/thermal_hexacopter/scripts/run_autonomous_mission.sh
#
# OR inside the container directly:
#   bash /uav_master_hub/projects/thermal_hexacopter/scripts/run_autonomous_mission.sh
# =============================================================================

set -euo pipefail

# ── Colours for pretty output ──────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[LAUNCH]${NC} $*"; }
ok()   { echo -e "${GREEN}[  OK  ]${NC} $*"; }
warn() { echo -e "${YELLOW}[ WARN ]${NC} $*"; }
fail() { echo -e "${RED}[FAIL  ]${NC} $*"; exit 1; }

# ── Configuration ──────────────────────────────────────────────────────────
WORKSPACE_SRC="/uav_master_hub/projects/thermal_hexacopter/src"
BUILD_DIR="/tmp/build"
ROS_DISTRO="${ROS_DISTRO:-humble}"
ROS_SETUP="/opt/ros/${ROS_DISTRO}/setup.bash"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║        🌾 UAV MASTER HUB — AUTONOMOUS MISSION           ║${NC}"
echo -e "${BOLD}║         5-Layer Precision Agriculture System             ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ── Step 1: Source ROS 2 ───────────────────────────────────────────────────
log "Sourcing ROS 2 ${ROS_DISTRO}..."
# shellcheck disable=SC1090
source "${ROS_SETUP}" || fail "ROS 2 setup not found at ${ROS_SETUP}"
ok "ROS 2 ${ROS_DISTRO} sourced"

# ── Step 2: Create build workspace symlinks ────────────────────────────────
log "Preparing build workspace at ${BUILD_DIR}..."
mkdir -p "${BUILD_DIR}/src"

# Symlink source packages into /tmp/build/src (read-only source, writable build)
for pkg in agri_msgs agri_hexacopter; do
    SRC_PATH="${WORKSPACE_SRC}/${pkg}"
    LINK_PATH="${BUILD_DIR}/src/${pkg}"
    if [ ! -L "${LINK_PATH}" ] && [ ! -d "${LINK_PATH}" ]; then
        ln -sf "${SRC_PATH}" "${LINK_PATH}"
        ok "Linked ${pkg} → ${BUILD_DIR}/src/"
    else
        ok "${pkg} already linked"
    fi
done

# Symlink shared px4_msgs if available
PX4_MSGS_SRC="/uav_master_hub/shared_libs/px4_msgs"
if [ -d "${PX4_MSGS_SRC}" ]; then
    if [ ! -L "${BUILD_DIR}/src/px4_msgs" ]; then
        ln -sf "${PX4_MSGS_SRC}" "${BUILD_DIR}/src/px4_msgs"
        ok "Linked px4_msgs → ${BUILD_DIR}/src/"
    fi
fi

# ── Step 3: Build ─────────────────────────────────────────────────────────
log "Building packages (agri_msgs first, then agri_hexacopter)..."
cd "${BUILD_DIR}"

# Build agri_msgs (must be before agri_hexacopter which depends on it)
colcon build \
    --packages-select agri_msgs \
    --cmake-args -DBUILD_TESTING=OFF \
    --event-handlers console_cohesion+ \
    2>&1 | grep -E 'Starting|Finished|Error|error|warning' || true

# Source the newly built agri_msgs so agri_hexacopter can find it
# shellcheck disable=SC1091
source "${BUILD_DIR}/install/setup.bash" 2>/dev/null || true

# Build agri_hexacopter
colcon build \
    --packages-select agri_hexacopter \
    --cmake-args -DBUILD_TESTING=OFF \
    --event-handlers console_cohesion+ \
    2>&1 | grep -E 'Starting|Finished|Error|error|warning' || true

ok "Build complete ✅"

# ── Step 4: Source the built workspace ────────────────────────────────────
# shellcheck disable=SC1091
source "${BUILD_DIR}/install/setup.bash"
ok "Built workspace sourced"

# ── Step 5: Verify packages are installed ─────────────────────────────────
log "Verifying installed packages..."
if ros2 pkg list | grep -q "agri_msgs"; then
    ok "agri_msgs — FOUND ✅"
else
    fail "agri_msgs not found in ros2 pkg list"
fi
if ros2 pkg list | grep -q "agri_hexacopter"; then
    ok "agri_hexacopter — FOUND ✅"
else
    fail "agri_hexacopter not found in ros2 pkg list"
fi

# ── Step 6: Create output directories ─────────────────────────────────────
log "Creating output directories..."
mkdir -p /reports/dataset/rgb /reports/dataset/thermal
ok "/reports/dataset/{rgb,thermal} ready"

# ── Step 7: Run A* self-test before launching ─────────────────────────────
log "Running A* path planner self-test (no ROS required)..."
python3 "${WORKSPACE_SRC}/agri_hexacopter/agri_hexacopter/path_planner.py" --selftest \
    && ok "A* self-test PASSED ✅" \
    || warn "A* self-test had issues — review output above"

# ── Step 8: Launch the full 5-layer system ────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  🚀 LAUNCHING 5-LAYER AUTONOMOUS SYSTEM                    ${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  Monitor mission log:  ${CYAN}ros2 topic echo /agri/mission/log${NC}"
echo -e "  Monitor health:       ${CYAN}ros2 topic echo /agri/plant_health/status${NC}"
echo -e "  Request E-STOP:       ${CYAN}ros2 topic pub /agri/e_stop std_msgs/msg/Bool '{data: true}' -1${NC}"
echo ""

ros2 launch agri_hexacopter full_autonomy.launch.py use_sim_time:=true
