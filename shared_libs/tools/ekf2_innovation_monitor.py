#!/usr/bin/env python3
"""
EKF2 Innovation Bounds Monitor - Real-time Flight Precision Audit
PhD Proof: Extended Kalman Filter stability monitoring for DIMENSION 2

This script monitors EKF2 innovation statistics during flight to validate
sensor fusion quality and flight control precision.

Author: Abhishek Raj, IIT Patna
Date: February 15, 2026
"""

import rclpy
from rclpy.node import Node
from px4_msgs.msg import EstimatorInnovations, EstimatorStatus
import numpy as np
from datetime import datetime


class EKF2InnovationMonitor(Node):
    """
    Monitors EKF2 innovation bounds in real-time during flight.
    
    Innovation = Measurement - Prediction
    Small innovations → Good sensor fusion
    Large innovations → Sensor issues or model mismatch
    """
    
    def __init__(self):
        super().__init__('ekf2_innovation_monitor')
        
        # Subscribe to EKF2 innovation topic
        self.innovation_sub = self.create_subscription(
            EstimatorInnovations,
            '/fmu/out/estimator_innovations',
            self.innovation_callback,
            10
        )
        
        # Subscribe to EKF2 status
        self.status_sub = self.create_subscription(
            EstimatorStatus,
            '/fmu/out/estimator_status',
            self.status_callback,
            10
        )
        
        # Innovation tracking
        self.innovation_history = {
            'gps_hpos': [],
            'gps_vpos': [],
            'gps_hvel': [],
            'gps_vvel': [],
            'baro_vpos': [],
            'flow': []
        }
        
        # EKF2 health flags
        self.ekf_healthy = False
        self.innovation_check_passed = False
        
        # Statistics
        self.sample_count = 0
        self.start_time = self.get_clock().now()
        
        # Create timer for periodic reporting (every 2 seconds)
        self.report_timer = self.create_timer(2.0, self.print_report)
        
        self.get_logger().info('🔍 EKF2 Innovation Monitor Started')
        self.get_logger().info('Monitoring innovation bounds for flight precision...')
        
    def innovation_callback(self, msg):
        """Process innovation data from EKF2"""
        self.sample_count += 1
        
        # GPS horizontal position innovation (meters)
        gps_hpos = np.sqrt(msg.gps_hpos[0]**2 + msg.gps_hpos[1]**2)
        self.innovation_history['gps_hpos'].append(gps_hpos)
        
        # GPS vertical position innovation (meters)
        self.innovation_history['gps_vpos'].append(abs(msg.gps_vpos))
        
        # GPS horizontal velocity innovation (m/s)
        gps_hvel = np.sqrt(msg.gps_hvel[0]**2 + msg.gps_hvel[1]**2)
        self.innovation_history['gps_hvel'].append(gps_hvel)
        
        # GPS vertical velocity innovation (m/s)
        self.innovation_history['gps_vvel'].append(abs(msg.gps_vvel))
        
        # Barometer vertical position innovation (meters)
        self.innovation_history['baro_vpos'].append(abs(msg.baro_vpos))
        
        # Optical flow innovation (rad/s)
        flow = np.sqrt(msg.flow[0]**2 + msg.flow[1]**2)
        self.innovation_history['flow'].append(flow)
        
        # Keep only last 100 samples (rolling window)
        for key in self.innovation_history:
            if len(self.innovation_history[key]) > 100:
                self.innovation_history[key] = self.innovation_history[key][-100:]
    
    def status_callback(self, msg):
        """Process EKF2 status flags"""
        # Check if EKF is healthy (bit flags)
        # Bit 0: Attitude valid
        # Bit 1: Velocity valid
        # Bit 2: Position valid
        self.ekf_healthy = (msg.filter_fault_flags == 0)
        self.innovation_check_passed = msg.innovation_check_flags == 0
    
    def print_report(self):
        """Print periodic innovation statistics report"""
        if self.sample_count == 0:
            self.get_logger().warn('⏳ Waiting for EKF2 data...')
            return
        
        # Calculate statistics
        stats = {}
        for key, values in self.innovation_history.items():
            if len(values) > 0:
                stats[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'max': np.max(values),
                    'current': values[-1]
                }
        
        # Print report
        print("\n" + "="*70)
        print(f"📊 EKF2 INNOVATION REPORT - Sample #{self.sample_count}")
        print(f"⏱️  Runtime: {(self.get_clock().now() - self.start_time).nanoseconds / 1e9:.1f}s")
        print("="*70)
        
        # GPS Position Innovations
        if 'gps_hpos' in stats:
            print(f"\n🛰️  GPS Horizontal Position Innovation:")
            print(f"   Current: {stats['gps_hpos']['current']:.3f} m")
            print(f"   Mean:    {stats['gps_hpos']['mean']:.3f} m")
            print(f"   Std Dev: {stats['gps_hpos']['std']:.3f} m")
            print(f"   Max:     {stats['gps_hpos']['max']:.3f} m")
            
            # Check against threshold (PX4 default: 0.5m)
            if stats['gps_hpos']['current'] > 0.5:
                print(f"   ⚠️  WARNING: Innovation exceeds 0.5m threshold!")
            else:
                print(f"   ✅ PASS: Within acceptable bounds")
        
        if 'gps_vpos' in stats:
            print(f"\n📏 GPS Vertical Position Innovation:")
            print(f"   Current: {stats['gps_vpos']['current']:.3f} m")
            print(f"   Mean:    {stats['gps_vpos']['mean']:.3f} m")
            print(f"   Max:     {stats['gps_vpos']['max']:.3f} m")
        
        # GPS Velocity Innovations
        if 'gps_hvel' in stats:
            print(f"\n🏃 GPS Horizontal Velocity Innovation:")
            print(f"   Current: {stats['gps_hvel']['current']:.3f} m/s")
            print(f"   Mean:    {stats['gps_hvel']['mean']:.3f} m/s")
            print(f"   Max:     {stats['gps_hvel']['max']:.3f} m/s")
        
        # Barometer Innovation
        if 'baro_vpos' in stats:
            print(f"\n🌡️  Barometer Vertical Position Innovation:")
            print(f"   Current: {stats['baro_vpos']['current']:.3f} m")
            print(f"   Mean:    {stats['baro_vpos']['mean']:.3f} m")
            print(f"   Max:     {stats['baro_vpos']['max']:.3f} m")
        
        # EKF Health Status
        print(f"\n🏥 EKF2 Health Status:")
        print(f"   Filter Healthy:       {'✅ YES' if self.ekf_healthy else '❌ NO'}")
        print(f"   Innovation Check:     {'✅ PASS' if self.innovation_check_passed else '❌ FAIL'}")
        
        # Overall Assessment
        print(f"\n🎯 PhD Flight Precision Assessment:")
        if self.ekf_healthy and self.innovation_check_passed:
            if 'gps_hpos' in stats and stats['gps_hpos']['mean'] < 0.3:
                print(f"   ✅ EXCELLENT: Mean innovation < 0.3m (High precision)")
            elif 'gps_hpos' in stats and stats['gps_hpos']['mean'] < 0.5:
                print(f"   ✅ GOOD: Mean innovation < 0.5m (Acceptable precision)")
            else:
                print(f"   ⚠️  FAIR: Innovation within bounds but elevated")
        else:
            print(f"   ❌ POOR: EKF2 health issues detected")
        
        print("="*70 + "\n")


def main(args=None):
    rclpy.init(args=args)
    
    monitor = EKF2InnovationMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("📊 FINAL EKF2 INNOVATION SUMMARY")
        print("="*70)
        
        # Print final statistics
        for key, values in monitor.innovation_history.items():
            if len(values) > 0:
                print(f"\n{key.upper()}:")
                print(f"  Mean:    {np.mean(values):.4f}")
                print(f"  Std Dev: {np.std(values):.4f}")
                print(f"  Min:     {np.min(values):.4f}")
                print(f"  Max:     {np.max(values):.4f}")
        
        print("\n" + "="*70)
        print(f"✅ Monitoring complete. Total samples: {monitor.sample_count}")
        print("="*70 + "\n")
    
    monitor.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
