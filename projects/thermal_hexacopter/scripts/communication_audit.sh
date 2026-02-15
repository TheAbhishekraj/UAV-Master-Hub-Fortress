#!/bin/bash

# communication_audit.sh
# Executes the "Communication Pillar" checks for DDS Topic verification.

# Detect Workspace Root
WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📍 Running Communication Audit in: $WORKSPACE_DIR"

echo ""
echo "🔍 Pillar 2: The Communication Pillar (DDS Topics)"
echo "Checking topic naming conventions in level1_basic_takeoff.py..."

# Path to the Python script
SCRIPT_PATH="$WORKSPACE_DIR/src/agri_hexacopter/agri_hexacopter/flight_levels/level1_basic_takeoff.py"

if [ -f "$SCRIPT_PATH" ]; then
    echo "Found script: $SCRIPT_PATH"
    echo "Scanning for publishers (checking /fmu/in/ vs /fmu/out/)..."
    grep "create_publisher" "$SCRIPT_PATH"
else
    echo "❌ Error: Python script not found at $SCRIPT_PATH"
    echo "   (You may need to create the 'level1_basic_takeoff.py' file first)"
fi