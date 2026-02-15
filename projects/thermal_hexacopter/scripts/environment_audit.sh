#!/bin/bash
# environment_audit.sh
# Detect Workspace Root
WORKSPACE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "📍 Running Environment Audit in: $WORKSPACE_DIR"
echo ""
echo "🔍 Pillar 3: The Environment Pillar (Maize Mesh)"
echo "Checking for local mesh URIs in bihar_maize.sdf..."
WORLD_FILE="$WORKSPACE_DIR/src/agri_hexacopter/worlds/bihar_maize.sdf"
if [ -f "$WORLD_FILE" ]; then
    # Action: grep "uri" ... | grep -v "fuel"
    grep "uri" "$WORLD_FILE" | grep -v "fuel"
else
    echo "❌ Error: World file not found at $WORLD_FILE"
fi