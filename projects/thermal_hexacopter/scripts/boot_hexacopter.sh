#!/bin/bash
# boot_hexacopter.sh - Robust Launch for Hexacopter Simulation

echo "🛑 Stopping old simulations..."
docker rm -f hexacopter_test hexacopter_gui 2>/dev/null

echo "🔓 Allowing Docker to use Display..."
xhost +local:root

echo "🚀 Launching Hexacopter Container (Detached)..."
# Start container in background, keeping it alive with tail
docker run -d --privileged --network=host \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd):/root/workspace \
    --name hexacopter_gui \
    hexacopter_lab_safe_copy \
    -c "tail -f /dev/null"

echo "⏳ Waiting for container to initialize..."
sleep 3

echo "🚁 Starting Simulation Script..."
# Execute the visual script inside the running container
docker exec hexacopter_gui /bin/bash -c "cd /root/workspace && chmod +x visual_hexacopter.sh && ./visual_hexacopter.sh"
