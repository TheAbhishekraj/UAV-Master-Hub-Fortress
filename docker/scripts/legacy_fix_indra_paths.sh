#!/bin/bash
# Fix all hardcoded paths in Indra-Eye project after moving to thermal_hexacopter_project

OLD_PATH="/home/abhishek/Downloads/indra_eye_project"
NEW_PATH="/home/abhishek/thermal_hexacopter_project/indra_eye_project"

cd /home/abhishek/thermal_hexacopter_project/indra_eye_project

echo "Fixing paths in all files..."

# Fix launch scripts
sed -i "s|$OLD_PATH|$NEW_PATH|g" launch_multi_terminal.sh
sed -i "s|$OLD_PATH|$NEW_PATH|g" launch_tmux.sh
sed -i "s|$OLD_PATH|$NEW_PATH|g" launch_docker.sh
sed -i "s|$OLD_PATH|$NEW_PATH|g" launch_docker_simple.sh
sed -i "s|$OLD_PATH|$NEW_PATH|g" run_mission.sh
sed -i "s|$OLD_PATH|$NEW_PATH|g" kill_and_fly.sh

# Fix Python scripts
sed -i "s|$OLD_PATH|$NEW_PATH|g" fly.py
sed -i "s|$OLD_PATH|$NEW_PATH|g" scripts/validate_system.py
sed -i "s|$OLD_PATH|$NEW_PATH|g" scripts/plot_trajectories.py

# Fix launch files
find src -name "*.py" -type f -exec sed -i "s|$OLD_PATH|$NEW_PATH|g" {} \;

# Fix YAML configs
find config -name "*.yaml" -type f -exec sed -i "s|$OLD_PATH|$NEW_PATH|g" {} \;

echo "✓ All paths updated!"
echo ""
echo "Verifying..."
grep -r "$OLD_PATH" . --include="*.sh" --include="*.py" --include="*.yaml" 2>/dev/null || echo "✓ No old paths found - all fixed!"
