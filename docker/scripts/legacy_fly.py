#!/usr/bin/env python3
"""
Indra-Eye Master Flight Launcher

One-command solution to launch, monitor, and record Indra-Eye missions.

Usage:
    python3 fly.py --mode sitl --qgc --record
    python3 fly.py --mode hitl --duration 600
    python3 fly.py --validate
"""

import argparse
import subprocess
import sys
import os
import time
import signal
from datetime import datetime
from pathlib import Path

class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

class IndraEyeLauncher:
    def __init__(self, args):
        self.args = args
        self.project_dir = Path("/home/abhishek/thermal_hexacopter_project")
        self.processes = []
        
    def print_header(self, msg):
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}{msg:^60}{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        
    def print_success(self, msg):
        print(f"{Colors.GREEN}[✓]{Colors.NC} {msg}")
        
    def print_error(self, msg):
        print(f"{Colors.RED}[✗]{Colors.NC} {msg}")
        
    def print_info(self, msg):
        print(f"{Colors.YELLOW}[INFO]{Colors.NC} {msg}")
        
    def print_step(self, msg):
        print(f"{Colors.CYAN}[STEP]{Colors.NC} {msg}")
    
    def run_command(self, cmd, check=True, shell=True, capture=False):
        """Run shell command"""
        try:
            if capture:
                result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=10)
                return result.stdout.strip() if result.returncode == 0 else None
            else:
                result = subprocess.run(cmd, shell=shell, check=check)
                return result.returncode == 0
        except Exception as e:
            self.print_error(f"Command failed: {e}")
            return False
    
    def validate_system(self):
        """Validate system before launch"""
        self.print_header("System Validation")
        
        checks = {
            "ROS 2 Humble": "test -f /opt/ros/humble/setup.bash",
            "Workspace built": f"test -d {self.project_dir}/install",
            "ES-EKF node": f"test -f {self.project_dir}/install/indra_eye_core/lib/indra_eye_core/es_ekf_node",
            "Config files": f"test -f {self.project_dir}/config/dds_bridge.yaml",
            "Launch files": f"test -f {self.project_dir}/src/indra_eye_sim/launch/sitl_launch.py"
        }
        
        all_passed = True
        for name, cmd in checks.items():
            if self.run_command(cmd, check=False):
                self.print_success(f"{name}")
            else:
                self.print_error(f"{name}")
                all_passed = False
        
        return all_passed
    
    def kill_existing_processes(self):
        """Kill all existing robotics processes"""
        self.print_step("Killing existing processes...")
        
        processes = ["gazebo", "gzserver", "gzclient", "px4", "MicroXRCEAgent", 
                    "mavros", "rviz2", "qgroundcontrol"]
        
        for proc in processes:
            self.run_command(f"killall -9 {proc} 2>/dev/null", check=False)
        
        time.sleep(2)
        self.print_success("All processes terminated")
    
    def source_workspace(self):
        """Source ROS 2 and workspace"""
        self.print_step("Sourcing workspace...")
        
        # Note: subprocess doesn't preserve environment, so we'll use bash -c
        return True
    
    def launch_sitl(self):
        """Launch SITL simulation"""
        self.print_header("Launching SITL Mission")
        
        # Build command
        cmd = f"cd {self.project_dir} && "
        cmd += "source /opt/ros/humble/setup.bash && "
        cmd += "source install/setup.bash && "
        cmd += "bash run_mission.sh --sitl"
        
        if self.args.qgc:
            cmd += " --qgc"
        if self.args.record:
            cmd += " --record"
        
        self.print_info(f"Command: {cmd}")
        
        # Launch in background
        proc = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        self.processes.append(proc)
        
        self.print_success(f"SITL launched (PID: {proc.pid})")
        
        return proc
    
    def launch_hitl(self):
        """Launch HITL mission"""
        self.print_header("Launching HITL Mission")
        
        # Check if in Docker
        if not os.path.exists('/.dockerenv'):
            self.print_error("HITL mode requires Docker environment")
            self.print_info("Run: docker-compose -f docker-compose.hitl.yaml up")
            return None
        
        # Build command
        cmd = f"cd {self.project_dir} && "
        cmd += "source /opt/ros/humble/setup.bash && "
        cmd += "source install/setup.bash && "
        cmd += "bash run_mission.sh --hitl"
        
        if self.args.qgc:
            cmd += " --qgc"
        
        # Launch
        proc = subprocess.Popen(cmd, shell=True, executable='/bin/bash')
        self.processes.append(proc)
        
        self.print_success(f"HITL launched (PID: {proc.pid})")
        
        return proc
    
    def monitor_mission(self, duration=None):
        """Monitor mission execution"""
        self.print_header("Mission Monitoring")
        
        self.print_info("Press Ctrl+C to stop mission")
        self.print_info("")
        self.print_info("Useful commands:")
        self.print_info("  - ros2 topic echo /indra_eye/diagnostics")
        self.print_info("  - ros2 topic echo /indra_eye/navigation_mode")
        self.print_info("  - ros2 topic pub /indra_eye/simulate_gps_denial std_msgs/Bool \"data: true\"")
        
        try:
            if duration:
                self.print_info(f"Mission will run for {duration} seconds")
                time.sleep(duration)
                self.print_success("Mission duration completed")
            else:
                # Wait indefinitely
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.print_info("\nMission interrupted by user")
    
    def cleanup(self):
        """Cleanup processes"""
        self.print_step("Cleaning up...")
        
        for proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                proc.kill()
        
        self.print_success("Cleanup complete")
    
    def run(self):
        """Main execution"""
        # Handle signals
        signal.signal(signal.SIGINT, lambda s, f: self.cleanup())
        signal.signal(signal.SIGTERM, lambda s, f: self.cleanup())
        
        try:
            # Validation
            if self.args.validate or self.args.mode is None:
                if self.validate_system():
                    self.print_success("\n✅ System validation passed!")
                    if self.args.validate:
                        return 0
                else:
                    self.print_error("\n❌ System validation failed!")
                    return 1
            
            # Kill existing processes
            if not self.args.no_kill:
                self.kill_existing_processes()
            
            # Launch based on mode
            if self.args.mode == 'sitl':
                proc = self.launch_sitl()
            elif self.args.mode == 'hitl':
                proc = self.launch_hitl()
            else:
                self.print_error(f"Unknown mode: {self.args.mode}")
                return 1
            
            if proc is None:
                return 1
            
            # Wait for initialization
            self.print_info("Waiting for initialization (10 seconds)...")
            time.sleep(10)
            
            # Monitor
            self.monitor_mission(self.args.duration)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Error: {e}")
            return 1
        finally:
            self.cleanup()

def main():
    parser = argparse.ArgumentParser(
        description='Indra-Eye Master Flight Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 fly.py --mode sitl --qgc --record
  python3 fly.py --mode hitl --duration 600
  python3 fly.py --validate
        """
    )
    
    parser.add_argument('--mode', choices=['sitl', 'hitl'], 
                       help='Launch mode (sitl or hitl)')
    parser.add_argument('--qgc', action='store_true',
                       help='Launch QGroundControl')
    parser.add_argument('--record', action='store_true',
                       help='Record mission to rosbag')
    parser.add_argument('--duration', type=int,
                       help='Mission duration in seconds')
    parser.add_argument('--validate', action='store_true',
                       help='Validate system only (no launch)')
    parser.add_argument('--no-kill', action='store_true',
                       help='Do not kill existing processes')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.validate and args.mode is None:
        parser.print_help()
        sys.exit(1)
    
    # Run launcher
    launcher = IndraEyeLauncher(args)
    sys.exit(launcher.run())

if __name__ == '__main__':
    main()
