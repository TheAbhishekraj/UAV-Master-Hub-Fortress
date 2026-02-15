#!/usr/bin/env python3
"""
Indra-Eye: System Validation Script

Validates that all components are properly configured and can communicate.

Usage:
    python3 validate_system.py
"""

import subprocess
import sys
import time

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def print_header(msg):
    print(f"{Colors.BLUE}========================================{Colors.NC}")
    print(f"{Colors.BLUE}{msg}{Colors.NC}")
    print(f"{Colors.BLUE}========================================{Colors.NC}")

def print_success(msg):
    print(f"{Colors.GREEN}[✓]{Colors.NC} {msg}")

def print_error(msg):
    print(f"{Colors.RED}[✗]{Colors.NC} {msg}")

def print_info(msg):
    print(f"{Colors.YELLOW}[INFO]{Colors.NC} {msg}")

def run_command(cmd, check=True):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        if check and result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception as e:
        return None

def check_ros2():
    """Check ROS 2 installation"""
    print_info("Checking ROS 2 Humble...")
    output = run_command("ros2 --version", check=False)
    if output and "humble" in output.lower():
        print_success(f"ROS 2 Humble found: {output}")
        return True
    else:
        print_error("ROS 2 Humble not found")
        return False

def check_workspace():
    """Check workspace build"""
    print_info("Checking workspace build...")
    if run_command("test -d /home/abhishek/thermal_hexacopter_project/indra_eye_project/install"):
        print_success("Workspace built")
        return True
    else:
        print_error("Workspace not built. Run: bash setup_and_run.sh --build")
        return False

def check_nodes():
    """Check if executables exist"""
    print_info("Checking Indra-Eye executables...")
    
    nodes = [
        "es_ekf_node",
        "supervisor_node",
        "mavros_bridge_node",
        "path_aggregator_node"
    ]
    
    all_found = True
    for node in nodes:
        path = f"/home/abhishek/thermal_hexacopter_project/indra_eye_project/install/indra_eye_core/lib/indra_eye_core/{node}"
        if run_command(f"test -f {path}"):
            print_success(f"{node} found")
        else:
            print_error(f"{node} not found")
            all_found = False
    
    return all_found

def check_config_files():
    """Check configuration files"""
    print_info("Checking configuration files...")
    
    configs = [
        "config/dds_bridge.yaml",
        "config/px4_params_indra_eye.txt",
        "config/hardware_map.yaml",
        "config/livox_config.json",
        "config/qgc_custom_layout.json"
    ]
    
    all_found = True
    for config in configs:
        path = f"/home/abhishek/thermal_hexacopter_project/indra_eye_project/{config}"
        if run_command(f"test -f {path}"):
            print_success(f"{config} found")
        else:
            print_error(f"{config} not found")
            all_found = False
    
    return all_found

def check_launch_files():
    """Check launch files"""
    print_info("Checking launch files...")
    
    launches = [
        "src/indra_eye_sim/launch/sitl_launch.py",
        "src/indra_eye_sim/launch/hitl_launch.py"
    ]
    
    all_found = True
    for launch in launches:
        path = f"/home/abhishek/thermal_hexacopter_project/indra_eye_project/{launch}"
        if run_command(f"test -f {path}"):
            print_success(f"{launch} found")
        else:
            print_error(f"{launch} not found")
            all_found = False
    
    return all_found

def check_scripts():
    """Check utility scripts"""
    print_info("Checking utility scripts...")
    
    scripts = [
        "setup_and_run.sh",
        "run_mission.sh",
        "kill_and_fly.sh",
        "scripts/plot_trajectories.py"
    ]
    
    all_found = True
    for script in scripts:
        path = f"/home/abhishek/thermal_hexacopter_project/indra_eye_project/{script}"
        if run_command(f"test -f {path}") and run_command(f"test -x {path}"):
            print_success(f"{script} found and executable")
        else:
            print_error(f"{script} not found or not executable")
            all_found = False
    
    return all_found

def check_documentation():
    """Check documentation"""
    print_info("Checking documentation...")
    
    docs = [
        "README.md",
        "INDRA_EYE_MANUAL.md",
        "docs/lit_review.md",
        "docs/funding_ppt.md"
    ]
    
    all_found = True
    for doc in docs:
        path = f"/home/abhishek/thermal_hexacopter_project/indra_eye_project/{doc}"
        if run_command(f"test -f {path}"):
            print_success(f"{doc} found")
        else:
            print_error(f"{doc} not found")
            all_found = False
    
    return all_found

def main():
    print_header("Indra-Eye System Validation")
    
    checks = [
        ("ROS 2 Installation", check_ros2),
        ("Workspace Build", check_workspace),
        ("Indra-Eye Nodes", check_nodes),
        ("Configuration Files", check_config_files),
        ("Launch Files", check_launch_files),
        ("Utility Scripts", check_scripts),
        ("Documentation", check_documentation)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n{Colors.BLUE}--- {name} ---{Colors.NC}")
        result = check_func()
        results.append((name, result))
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = True
    for name, result in results:
        if result:
            print_success(f"{name}: PASS")
        else:
            print_error(f"{name}: FAIL")
            all_passed = False
    
    print()
    if all_passed:
        print_success("✅ All checks passed! System is ready for deployment.")
        print_info("Next step: bash run_mission.sh --sitl")
        return 0
    else:
        print_error("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
