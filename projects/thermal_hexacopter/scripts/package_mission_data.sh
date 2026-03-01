#!/usr/bin/env bash
# =============================================================================
# package_mission_data.sh - The "Mission Success" Script
# =============================================================================
# Packages all images and logs from /reports/dataset into a final zip bundle
# ready for the thesis.

echo "📦 Packaging Mission Data..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="/tmp/bihar_mission_data_${TIMESTAMP}.zip"

# Ensure the zip utility is available
if ! command -v zip &> /dev/null; then
    echo "Installing zip utility..."
    apt-get update && apt-get install -y zip > /dev/null 2>&1
fi

if [ -d "/reports/dataset" ]; then
    echo "📸 Found /reports/dataset directory. Zipping contents..."
    cd /reports/dataset
    zip -r "${ARCHIVE_NAME}" ./* > /dev/null 2>&1
    
    echo "✅ Mission data successfully zipped to:"
    echo "   📁 ${ARCHIVE_NAME}"
    echo "This file is ready to be moved to your host machine for your thesis."
else
    echo "⚠️ Warning: Directory /reports/dataset not found!"
    echo "Make sure the drone has completed its image collection phase."
fi
