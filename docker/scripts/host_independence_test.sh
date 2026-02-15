#!/bin/bash
# 🛸 HOST INDEPENDENCE TEST (PhD Validation)
# Purpose: Proves the Hub image is self-contained (Baked-In Logic)

HUB_DIR="/home/abhishek/uav_master_hub"
BACKUP_DIR="/home/abhishek/uav_master_hub_BACKUP"

echo "================================================================"
echo "🧪 STARTING INDEPENDENCE TEST (BAKING-IN VERIFICATION)"
echo "================================================================"

# 1. Verification of Image existence
if [[ "$(docker images -q uav_hub_golden:v4 2> /dev/null)" == "" ]]; then
    echo "❌ ERROR: uav_hub_golden:v4 not found. Build must complete first."
    exit 1
fi

# 2. Rename High-Value Target
echo "Step 1: Renaming host directory to simulate file movement..."
mv "$HUB_DIR" "$BACKUP_DIR"
echo "✅ Directory moved to $BACKUP_DIR"

# 3. Launch Attempt
echo "Step 2: Launching container from independent image..."
echo "---"
# Use docker run instead of compose because compose file is inside the renamed directory
docker run --rm --privileged \
    --network host \
    -e DISPLAY=$DISPLAY \
    -e XAUTHORITY=/tmp/.docker.xauth \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v /tmp/.docker.xauth:/tmp/.docker.xauth:rw \
    -v /dev/shm:/dev/shm \
    --device /dev/dri:/dev/dri \
    uav_hub_golden:v4 \
    /root/uav_master_hub/scripts/verify_fortress_integrity.sh

RESULT=$?

# 4. Restore
echo "---"
echo "Step 3: Restoring host environment..."
mv "$BACKUP_DIR" "$HUB_DIR"
echo "✅ Directory restored."

if [ $RESULT -eq 0 ]; then
    echo "================================================================"
    echo "🎉 SUCCESS: BAKING-IN LOGIC VERIFIED"
    echo "The Hub is independent of its birthplace."
    echo "================================================================"
else
    echo "================================================================"
    echo "❌ FAILURE: Independence check failed."
    echo "================================================================"
fi
