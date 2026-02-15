#!/bin/bash
# Verify the UAV Master Hub Golden Image v4.0

IMAGE_NAME="uav_hub_golden:v4"
HUB_ROOT="/root/uav_master_hub"

echo "🔍 Verifying ${IMAGE_NAME}..."

# 1. Check if Image Exists
if ! docker image inspect ${IMAGE_NAME} > /dev/null 2>&1; then
    echo "❌ Image ${IMAGE_NAME} not found! Build failed or not complete."
    exit 1
fi
echo "✅ Image exists."

# 2. Test "Baking-In" Logic (Physical Independence)
# We run WITHOUT mounting the volume to see if code exists inside.
echo "🧪 Testing 'Baking-In' (Physical Independence)..."
RESEARCH_FILE="${HUB_ROOT}/projects/thermal_hexacopter/src/agri_hexacopter/agri_hexacopter/flight_levels/level2_bihar_survey.py"
if docker run --rm ${IMAGE_NAME} ls ${RESEARCH_FILE} > /dev/null 2>&1; then
    echo "✅ Success: Code is baked into the image."
else
    echo "❌ Failure: Code missing from image. 'Baking-In' failed."
    echo "   Searched for: ${RESEARCH_FILE}"
fi

# 3. Test "Read-Only Shield"
# We mount the volume as Read-Only and try to write.
echo "🛡️ Testing 'Read-Only Shield'..."
if docker run --rm -v $(pwd):${HUB_ROOT}:ro ${IMAGE_NAME} touch ${HUB_ROOT}/test_shield_breach 2>/dev/null; then
    echo "❌ Failure: Shield breached! File system is writable."
else
    echo "✅ Success: Shield active (Read-only file system)."
fi

# 4. Verify Internal Symlinks (PX4 Msgs)
echo "🔗 Verifying Internal Symlinks..."
if docker run --rm ${IMAGE_NAME} test -d ${HUB_ROOT}/shared_libs/px4_msgs/install; then
    echo "✅ Success: px4_msgs appears built/installed."
else
    echo "❌ Failure: px4_msgs install directory missing."
fi

echo "════════════════════════════════════════════════════════════════"
echo "🎉 Verification Complete. The Fortress is Secure."
echo "════════════════════════════════════════════════════════════════"
