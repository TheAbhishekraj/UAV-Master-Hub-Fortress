#!/usr/bin/env python3
"""
Hover Stability Monitor - Real-time Position Error & Innovation Tracking
PhD Proof: Flight precision and control loop stability for DIMENSION 2

Monitors VehicleLocalPosition and EstimatorInnovations during 5m hover test
to quantify position error and sensor fusion quality.

Author: Abhishek Raj, IIT Patna
Date: February 15, 2026
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import VehicleLocalPosition, EstimatorInnovations
import numpy as np
from datetime import datetime
import time


class HoverStabilityMonitor(Node):
    """
    Monitors position error and EKF2 innovations during hover.
    
    Position Error = Actual Position - Target Position
    Small error → Good control loop performance
    
    Innovation = Measurement - Prediction  
    Small innovation → Good sensor fusion
    """
    
    def __init__(self):
        super().__init__('hover_stability_monitor')
        
        # Configure QoS for PX4
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # Subscribe to vehicle position
        self.position_sub = self.create_subscription(
            VehicleLocalPosition,
            '/fmu/out/vehicle_local_position',
            self.position_callback,
            qos_profile
        )
        
        # Subscribe to EKF2 innovations
        self.innovation_sub = self.create_subscription(
            EstimatorInnovations,
            '/fmu/out/estimator_innovations',
            self.innovation_callback,
            qos_profile
        )
        
        # Target hover position (NED frame)
        self.target_x = 0.0  # meters
        self.target_y = 0.0  # meters
        self.target_z = -5.0  # meters (5m altitude, NED: negative is up)
        
        # Position error tracking
        self.position_errors = {
            'x': [],
            'y': [],
            'z': [],
            'horizontal': [],  # sqrt(x^2 + y^2)
            'total': []  # sqrt(x^2 + y^2 + z^2)
        }
        
        # Innovation tracking
        self.innovations = {
            'gps_hpos': [],
            'gps_vpos': []
        }
        
        # Current state
        self.current_position = None
        self.current_innovation = None
        self.sample_count = 0
        self.start_time = None
        
        # Statistics
        self.hover_started = False
        self.hover_start_time = None
        
        # Create timer for reporting (every 1 second)
        self.report_timer = self.create_timer(1.0, self.print_report)
        
        self.get_logger().info('🎯 Hover Stability Monitor Started')
        self.get_logger().info(f'Target Position: X={self.target_x}m, Y={self.target_y}m, Z={self.target_z}m')
        self.get_logger().info('Monitoring position error and innovations...')
        
    def position_callback(self, msg):
        """Process position data"""
        if self.start_time is None:
            self.start_time = time.time()
        
        self.sample_count += 1
        self.current_position = msg
        
        # Calculate position errors (actual - target)
        error_x = msg.x - self.target_x
        error_y = msg.y - self.target_y
        error_z = msg.z - self.target_z
        
        # Calculate derived errors
        error_horizontal = np.sqrt(error_x**2 + error_y**2)
        error_total = np.sqrt(error_x**2 + error_y**2 + error_z**2)
        
        # Store errors
        self.position_errors['x'].append(error_x)
        self.position_errors['y'].append(error_y)
        self.position_errors['z'].append(error_z)
        self.position_errors['horizontal'].append(error_horizontal)
        self.position_errors['total'].append(error_total)
        
        # Detect hover start (when altitude reaches target ±0.5m)
        if not self.hover_started and abs(error_z) < 0.5:
            self.hover_started = True
            self.hover_start_time = time.time()
            self.get_logger().info('✅ Hover altitude reached! Starting precision monitoring...')
        
        # Keep only last 100 samples (rolling window)
        for key in self.position_errors:
            if len(self.position_errors[key]) > 100:
                self.position_errors[key] = self.position_errors[key][-100:]
    
    def innovation_callback(self, msg):
        """Process innovation data"""
        self.current_innovation = msg
        
        # GPS horizontal position innovation
        gps_hpos = np.sqrt(msg.gps_hpos[0]**2 + msg.gps_hpos[1]**2)
        self.innovations['gps_hpos'].append(gps_hpos)
        
        # GPS vertical position innovation
        self.innovations['gps_vpos'].append(abs(msg.gps_vpos))
        
        # Keep only last 100 samples
        for key in self.innovations:
            if len(self.innovations[key]) > 100:
                self.innovations[key] = self.innovations[key][-100:]
    
    def print_report(self):
        """Print periodic stability report"""
        if self.current_position is None:
            self.get_logger().warn('⏳ Waiting for position data...')
            return
        
        runtime = time.time() - self.start_time if self.start_time else 0
        
        # Calculate statistics
        pos_stats = {}
        for key, values in self.position_errors.items():
            if len(values) > 0:
                pos_stats[key] = {
                    'current': values[-1],
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'max': np.max(values),
                    'rms': np.sqrt(np.mean(np.array(values)**2))  # Root Mean Square
                }
        
        innov_stats = {}
        for key, values in self.innovations.items():
            if len(values) > 0:
                innov_stats[key] = {
                    'current': values[-1],
                    'mean': np.mean(values),
                    'max': np.max(values)
                }
        
        # Print report
        print("\n" + "="*75)
        print(f"📊 HOVER STABILITY REPORT - Sample #{self.sample_count}")
        print(f"⏱️  Runtime: {runtime:.1f}s", end="")
        if self.hover_started:
            hover_time = time.time() - self.hover_start_time
            print(f" | Hover Time: {hover_time:.1f}s")
        else:
            print(" | Status: Climbing to target altitude...")
        print("="*75)
        
        # Current Position
        print(f"\n📍 Current Position (NED):")
        print(f"   X: {self.current_position.x:7.3f} m  (Target: {self.target_x:.1f} m)")
        print(f"   Y: {self.current_position.y:7.3f} m  (Target: {self.target_y:.1f} m)")
        print(f"   Z: {self.current_position.z:7.3f} m  (Target: {self.target_z:.1f} m)")
        print(f"   Altitude: {-self.current_position.z:.3f} m (AGL)")
        
        # Position Errors
        if 'horizontal' in pos_stats:
            print(f"\n📏 Position Error Statistics:")
            print(f"   Horizontal Error:")
            print(f"      Current: {pos_stats['horizontal']['current']:.3f} m")
            print(f"      Mean:    {pos_stats['horizontal']['mean']:.3f} m")
            print(f"      RMS:     {pos_stats['horizontal']['rms']:.3f} m")
            print(f"      Std Dev: {pos_stats['horizontal']['std']:.3f} m")
            print(f"      Max:     {pos_stats['horizontal']['max']:.3f} m")
            
            # Assessment
            if pos_stats['horizontal']['rms'] < 0.1:
                print(f"      ✅ EXCELLENT: RMS < 0.1m (PhD-grade precision)")
            elif pos_stats['horizontal']['rms'] < 0.3:
                print(f"      ✅ GOOD: RMS < 0.3m (Acceptable precision)")
            elif pos_stats['horizontal']['rms'] < 0.5:
                print(f"      ⚠️  FAIR: RMS < 0.5m (Marginal precision)")
            else:
                print(f"      ❌ POOR: RMS > 0.5m (Insufficient precision)")
        
        if 'z' in pos_stats:
            print(f"\n   Vertical Error:")
            print(f"      Current: {pos_stats['z']['current']:.3f} m")
            print(f"      Mean:    {pos_stats['z']['mean']:.3f} m")
            print(f"      RMS:     {pos_stats['z']['rms']:.3f} m")
            print(f"      Max:     {pos_stats['z']['max']:.3f} m")
        
        # Velocity (for stability assessment)
        print(f"\n🏃 Current Velocity (NED):")
        print(f"   VX: {self.current_position.vx:6.3f} m/s")
        print(f"   VY: {self.current_position.vy:6.3f} m/s")
        print(f"   VZ: {self.current_position.vz:6.3f} m/s")
        v_horizontal = np.sqrt(self.current_position.vx**2 + self.current_position.vy**2)
        print(f"   Horizontal Speed: {v_horizontal:.3f} m/s")
        
        if v_horizontal < 0.1:
            print(f"   ✅ STABLE: Velocity < 0.1 m/s (stationary hover)")
        elif v_horizontal < 0.3:
            print(f"   ⚠️  DRIFTING: Velocity < 0.3 m/s (minor drift)")
        else:
            print(f"   ❌ UNSTABLE: Velocity > 0.3 m/s (significant drift)")
        
        # EKF2 Innovations
        if innov_stats:
            print(f"\n🔍 EKF2 Innovation (Sensor Fusion Quality):")
            if 'gps_hpos' in innov_stats:
                print(f"   GPS Horizontal:")
                print(f"      Current: {innov_stats['gps_hpos']['current']:.3f} m")
                print(f"      Mean:    {innov_stats['gps_hpos']['mean']:.3f} m")
                print(f"      Max:     {innov_stats['gps_hpos']['max']:.3f} m")
                
                if innov_stats['gps_hpos']['mean'] < 0.3:
                    print(f"      ✅ EXCELLENT: Innovation < 0.3m")
                elif innov_stats['gps_hpos']['mean'] < 0.5:
                    print(f"      ✅ GOOD: Innovation < 0.5m")
                else:
                    print(f"      ⚠️  ELEVATED: Innovation > 0.5m")
        
        # Overall Assessment
        print(f"\n🎯 PhD Hover Precision Assessment:")
        if self.hover_started and 'horizontal' in pos_stats:
            rms_error = pos_stats['horizontal']['rms']
            mean_innov = innov_stats.get('gps_hpos', {}).get('mean', 999)
            
            if rms_error < 0.1 and mean_innov < 0.3 and v_horizontal < 0.1:
                print(f"   ✅ EXCELLENT: PhD-grade precision achieved")
                print(f"      • Position RMS: {rms_error:.3f}m < 0.1m")
                print(f"      • Innovation: {mean_innov:.3f}m < 0.3m")
                print(f"      • Velocity: {v_horizontal:.3f}m/s < 0.1m/s")
            elif rms_error < 0.3 and mean_innov < 0.5:
                print(f"   ✅ GOOD: Acceptable for research validation")
            else:
                print(f"   ⚠️  NEEDS TUNING: Consider PID parameter adjustment")
        else:
            print(f"   ⏳ Waiting for hover stabilization...")
        
        print("="*75 + "\n")


def main(args=None):
    rclpy.init(args=args)
    
    monitor = HoverStabilityMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        print("\n\n" + "="*75)
        print("📊 FINAL HOVER STABILITY SUMMARY")
        print("="*75)
        
        # Print final statistics
        if monitor.hover_started:
            hover_duration = time.time() - monitor.hover_start_time
            print(f"\n⏱️  Total Hover Time: {hover_duration:.1f} seconds")
        
        print(f"\n📏 Position Error Statistics:")
        for key in ['horizontal', 'z', 'total']:
            if key in monitor.position_errors and len(monitor.position_errors[key]) > 0:
                values = monitor.position_errors[key]
                print(f"\n{key.upper()} Error:")
                print(f"  Mean:    {np.mean(values):.4f} m")
                print(f"  RMS:     {np.sqrt(np.mean(np.array(values)**2)):.4f} m")
                print(f"  Std Dev: {np.std(values):.4f} m")
                print(f"  Min:     {np.min(values):.4f} m")
                print(f"  Max:     {np.max(values):.4f} m")
        
        print("\n" + "="*75)
        print(f"✅ Monitoring complete. Total samples: {monitor.sample_count}")
        print("="*75 + "\n")
    
    monitor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
