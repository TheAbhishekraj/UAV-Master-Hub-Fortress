#!/bin/bash
# Export the UAV Master Hub Golden Image to a portable archive

IMAGE_NAME="uav_hub_golden:v4"
OUTPUT_FILE="PhD_Master_Hub.tar.gz"

echo "📦 Exporting ${IMAGE_NAME} to ${OUTPUT_FILE}..."
echo "⏳ This may take a while depending on image size..."

docker save ${IMAGE_NAME} | gzip > ${OUTPUT_FILE}

if [ $? -eq 0 ]; then
    echo "✅ Export Complete: ${OUTPUT_FILE}"
    echo "   Size: $(du -h ${OUTPUT_FILE} | cut -f1)"
    echo "   To restore: docker load < ${OUTPUT_FILE}"
else
    echo "❌ Export Failed!"
    exit 1
fi
