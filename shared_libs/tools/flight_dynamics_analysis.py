#!/usr/bin/env python3
"""
Flight Dynamics Analysis Tool for PX4 Telemetry
================================================

Purpose: Parse PX4 .ulg telemetry logs to analyze flight dynamics, EKF2 sensor fusion,
         and generate Bode plots + step response curves for altitude hold performance.

Author: Abhishek Raj - PhD Research (IIT Patna)
Project: Autonomous Thermal-Imaging Hexacopter for Precision Agriculture
Date: February 15, 2026

Requirements:
    pip install pyulog matplotlib numpy scipy pandas

Usage:
    python flight_dynamics_analysis.py <path_to_log.ulg>

Output:
    - Bode plots (altitude_bode_plot.png)
    - Step response curves (altitude_step_response.png)
    - EKF2 sensor fusion analysis (ekf2_analysis.txt)
    - Flight dynamics report (flight_dynamics_report.md)
"""

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal
from pyulog import ULog

class FlightDynamicsAnalyzer:
    """Analyze PX4 flight dynamics from .ulg telemetry logs."""
    
    def __init__(self, log_file):
        """Initialize analyzer with ULog file."""
        self.log_file = Path(log_file)
        if not self.log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        print(f"📂 Loading ULog file: {self.log_file.name}")
        self.ulog = ULog(str(self.log_file))
        self.output_dir = self.log_file.parent / f"{self.log_file.stem}_analysis"
        self.output_dir.mkdir(exist_ok=True)
        
        # Data storage
        self.position_data = None
        self.attitude_data = None
        self.sensor_data = None
        self.ekf2_data = None
        
    def extract_data(self):
        """Extract relevant data from ULog."""
        print("🔍 Extracting telemetry data...")
        
        # Extract vehicle local position
        try:
            pos_msg = self.ulog.get_dataset('vehicle_local_position')
            self.position_data = pd.DataFrame({
                'timestamp': pos_msg.data['timestamp'] / 1e6,  # Convert to seconds
                'x': pos_msg.data['x'],
                'y': pos_msg.data['y'],
                'z': pos_msg.data['z'],  # NED: negative is up
                'vx': pos_msg.data['vx'],
                'vy': pos_msg.data['vy'],
                'vz': pos_msg.data['vz']
            })
            print(f"  ✅ Extracted {len(self.position_data)} position samples")
        except Exception as e:
            print(f"  ⚠️  Position data not available: {e}")
        
        # Extract attitude
        try:
            att_msg = self.ulog.get_dataset('vehicle_attitude')
            self.attitude_data = pd.DataFrame({
                'timestamp': att_msg.data['timestamp'] / 1e6,
                'roll': np.degrees(att_msg.data['rollspeed']),  # Convert to degrees
                'pitch': np.degrees(att_msg.data['pitchspeed']),
                'yaw': np.degrees(att_msg.data['yawspeed'])
            })
            print(f"  ✅ Extracted {len(self.attitude_data)} attitude samples")
        except Exception as e:
            print(f"  ⚠️  Attitude data not available: {e}")
        
        # Extract sensor combined (IMU)
        try:
            sensor_msg = self.ulog.get_dataset('sensor_combined')
            self.sensor_data = pd.DataFrame({
                'timestamp': sensor_msg.data['timestamp'] / 1e6,
                'gyro_x': sensor_msg.data['gyro_rad[0]'],
                'gyro_y': sensor_msg.data['gyro_rad[1]'],
                'gyro_z': sensor_msg.data['gyro_rad[2]'],
                'accel_x': sensor_msg.data['accelerometer_m_s2[0]'],
                'accel_y': sensor_msg.data['accelerometer_m_s2[1]'],
                'accel_z': sensor_msg.data['accelerometer_m_s2[2]']
            })
            print(f"  ✅ Extracted {len(self.sensor_data)} sensor samples")
        except Exception as e:
            print(f"  ⚠️  Sensor data not available: {e}")
        
        # Extract EKF2 estimator status
        try:
            ekf_msg = self.ulog.get_dataset('estimator_status')
            self.ekf2_data = pd.DataFrame({
                'timestamp': ekf_msg.data['timestamp'] / 1e6,
                'pos_horiz_accuracy': ekf_msg.data['pos_horiz_accuracy'],
                'pos_vert_accuracy': ekf_msg.data['pos_vert_accuracy']
            })
            print(f"  ✅ Extracted {len(self.ekf2_data)} EKF2 samples")
        except Exception as e:
            print(f"  ⚠️  EKF2 data not available: {e}")
    
    def analyze_imu_noise(self):
        """Analyze IMU noise characteristics."""
        if self.sensor_data is None:
            print("⚠️  Skipping IMU noise analysis - no sensor data")
            return None
        
        print("\n📊 Analyzing IMU Noise...")
        
        # Calculate noise statistics
        gyro_noise = {
            'x_std': self.sensor_data['gyro_x'].std(),
            'y_std': self.sensor_data['gyro_y'].std(),
            'z_std': self.sensor_data['gyro_z'].std()
        }
        
        accel_noise = {
            'x_std': self.sensor_data['accel_x'].std(),
            'y_std': self.sensor_data['accel_y'].std(),
            'z_std': self.sensor_data['accel_z'].std()
        }
        
        print(f"  Gyro Noise (rad/s): X={gyro_noise['x_std']:.4f}, Y={gyro_noise['y_std']:.4f}, Z={gyro_noise['z_std']:.4f}")
        print(f"  Accel Noise (m/s²): X={accel_noise['x_std']:.4f}, Y={accel_noise['y_std']:.4f}, Z={accel_noise['z_std']:.4f}")
        
        return {'gyro': gyro_noise, 'accel': accel_noise}
    
    def analyze_altitude_hold(self):
        """Analyze altitude hold performance - step response and steady-state error."""
        if self.position_data is None:
            print("⚠️  Skipping altitude analysis - no position data")
            return None
        
        print("\n📊 Analyzing Altitude Hold Performance...")
        
        # Convert NED z to altitude (positive up)
        altitude = -self.position_data['z'].values
        time = self.position_data['timestamp'].values
        time = time - time[0]  # Start from t=0
        
        # Detect setpoint (assume target is most common altitude during hover)
        from scipy.stats import mode
        setpoint = mode(np.round(altitude)).mode[0]
        
        print(f"  Detected hover setpoint: {setpoint:.2f} m")
        
        # Find step response (when altitude first approaches setpoint)
        target_reached_idx = np.where(np.abs(altitude - setpoint) < 0.5)[0]
        if len(target_reached_idx) > 0:
            step_start = max(0, target_reached_idx[0] - 50)  # Include ramp-up
            step_end = min(len(altitude), target_reached_idx[-1] + 50)
            
            step_time = time[step_start:step_end]
            step_altitude = altitude[step_start:step_end]
            
            # Calculate metrics
            steady_state = np.mean(step_altitude[-100:])  # Last 100 samples
            steady_state_error = abs(steady_state - setpoint)
            
            # Settling time (time to reach ±2% of setpoint)
            settling_threshold = 0.02 * setpoint
            settled_idx = np.where(np.abs(step_altitude - setpoint) < settling_threshold)[0]
            settling_time = step_time[settled_idx[0]] - step_time[0] if len(settled_idx) > 0 else None
            
            # Overshoot
            overshoot = (np.max(step_altitude) - setpoint) / setpoint * 100 if np.max(step_altitude) > setpoint else 0
            
            print(f"  Steady-State Altitude: {steady_state:.2f} m")
            print(f"  Steady-State Error: {steady_state_error:.2f} m ({steady_state_error/setpoint*100:.1f}%)")
            print(f"  Settling Time (±2%): {settling_time:.2f} s" if settling_time else "  Settling Time: Not achieved")
            print(f"  Overshoot: {overshoot:.1f}%")
            
            # Plot step response
            plt.figure(figsize=(10, 6))
            plt.plot(step_time, step_altitude, 'b-', linewidth=2, label='Actual Altitude')
            plt.axhline(y=setpoint, color='r', linestyle='--', label=f'Setpoint ({setpoint:.1f} m)')
            plt.axhline(y=setpoint + settling_threshold, color='g', linestyle=':', alpha=0.5, label='±2% Band')
            plt.axhline(y=setpoint - settling_threshold, color='g', linestyle=':', alpha=0.5)
            plt.xlabel('Time (s)', fontsize=12)
            plt.ylabel('Altitude (m)', fontsize=12)
            plt.title('Altitude Step Response - 5m Hover Test', fontsize=14, fontweight='bold')
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            
            step_response_file = self.output_dir / 'altitude_step_response.png'
            plt.savefig(step_response_file, dpi=300)
            print(f"  💾 Saved: {step_response_file}")
            plt.close()
            
            return {
                'setpoint': setpoint,
                'steady_state': steady_state,
                'steady_state_error': steady_state_error,
                'settling_time': settling_time,
                'overshoot': overshoot
            }
        else:
            print("  ⚠️  Could not detect stable hover period")
            return None
    
    def generate_bode_plot(self):
        """Generate Bode plot for altitude control system."""
        if self.position_data is None:
            print("⚠️  Skipping Bode plot - no position data")
            return
        
        print("\n📊 Generating Bode Plot...")
        
        # Use altitude and vertical velocity for frequency analysis
        altitude = -self.position_data['z'].values
        vz = -self.position_data['vz'].values
        time = self.position_data['timestamp'].values
        time = time - time[0]
        
        # Calculate sample rate
        dt = np.mean(np.diff(time))
        fs = 1 / dt
        
        print(f"  Sample rate: {fs:.1f} Hz")
        
        # Estimate transfer function using FFT
        from scipy.fft import fft, fftfreq
        
        # Apply window to reduce spectral leakage
        window = signal.windows.hann(len(altitude))
        altitude_fft = fft(altitude * window)
        vz_fft = fft(vz * window)
        
        freq = fftfreq(len(altitude), dt)
        freq = freq[:len(freq)//2]  # Take positive frequencies only
        
        # Magnitude (dB)
        H = altitude_fft / (vz_fft + 1e-10)  # Avoid division by zero
        magnitude_db = 20 * np.log10(np.abs(H[:len(freq)]) + 1e-10)
        phase_deg = np.angle(H[:len(freq)]) * 180 / np.pi
        
        # Plot Bode diagram
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # Magnitude plot
        ax1.semilogx(freq[1:], magnitude_db[1:], 'b-', linewidth=2)
        ax1.set_ylabel('Magnitude (dB)', fontsize=12)
        ax1.set_title('Altitude Control - Bode Plot', fontsize=14, fontweight='bold')
        ax1.grid(True, which='both', alpha=0.3)
        
        # Phase plot
        ax2.semilogx(freq[1:], phase_deg[1:], 'r-', linewidth=2)
        ax2.set_xlabel('Frequency (Hz)', fontsize=12)
        ax2.set_ylabel('Phase (degrees)', fontsize=12)
        ax2.grid(True, which='both', alpha=0.3)
        
        plt.tight_layout()
        
        bode_file = self.output_dir / 'altitude_bode_plot.png'
        plt.savefig(bode_file, dpi=300)
        print(f"  💾 Saved: {bode_file}")
        plt.close()
    
    def generate_report(self, imu_noise, altitude_metrics):
        """Generate comprehensive flight dynamics report."""
        print("\n📝 Generating Flight Dynamics Report...")
        
        report_file = self.output_dir / 'flight_dynamics_report.md'
        
        with open(report_file, 'w') as f:
            f.write("# Flight Dynamics Analysis Report\n\n")
            f.write(f"**Log File**: {self.log_file.name}\n")
            f.write(f"**Analysis Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 1. IMU Noise Characteristics\n\n")
            if imu_noise:
                f.write("### Gyroscope Noise (rad/s)\n")
                f.write(f"- X-axis: {imu_noise['gyro']['x_std']:.4f}\n")
                f.write(f"- Y-axis: {imu_noise['gyro']['y_std']:.4f}\n")
                f.write(f"- Z-axis: {imu_noise['gyro']['z_std']:.4f}\n\n")
                
                f.write("### Accelerometer Noise (m/s²)\n")
                f.write(f"- X-axis: {imu_noise['accel']['x_std']:.4f}\n")
                f.write(f"- Y-axis: {imu_noise['accel']['y_std']:.4f}\n")
                f.write(f"- Z-axis: {imu_noise['accel']['z_std']:.4f}\n\n")
            else:
                f.write("*IMU data not available*\n\n")
            
            f.write("## 2. Altitude Hold Performance\n\n")
            if altitude_metrics:
                f.write(f"**Setpoint**: {altitude_metrics['setpoint']:.2f} m\n\n")
                f.write(f"**Steady-State Altitude**: {altitude_metrics['steady_state']:.2f} m\n\n")
                f.write(f"**Steady-State Error**: {altitude_metrics['steady_state_error']:.2f} m ")
                f.write(f"({altitude_metrics['steady_state_error']/altitude_metrics['setpoint']*100:.1f}%)\n\n")
                
                if altitude_metrics['settling_time']:
                    f.write(f"**Settling Time (±2%)**: {altitude_metrics['settling_time']:.2f} s\n\n")
                else:
                    f.write("**Settling Time**: Not achieved\n\n")
                
                f.write(f"**Overshoot**: {altitude_metrics['overshoot']:.1f}%\n\n")
                
                f.write("### Step Response\n\n")
                f.write(f"![Altitude Step Response](altitude_step_response.png)\n\n")
            else:
                f.write("*Altitude data not available or hover not detected*\n\n")
            
            f.write("## 3. Frequency Domain Analysis\n\n")
            f.write("### Bode Plot\n\n")
            f.write(f"![Altitude Bode Plot](altitude_bode_plot.png)\n\n")
            
            f.write("## 4. Recommendations\n\n")
            if altitude_metrics and altitude_metrics['steady_state_error'] > 0.5:
                f.write("- ⚠️ **High steady-state error detected** - Consider tuning altitude PID controller\n")
            if altitude_metrics and altitude_metrics['overshoot'] > 10:
                f.write("- ⚠️ **Significant overshoot detected** - Reduce proportional gain or add derivative control\n")
            if imu_noise and imu_noise['gyro']['z_std'] > 0.05:
                f.write("- ⚠️ **High gyro noise** - Check sensor calibration or add filtering\n")
            
            if altitude_metrics and altitude_metrics['steady_state_error'] < 0.2:
                f.write("- ✅ **Excellent altitude hold performance**\n")
            
            f.write("\n---\n\n")
            f.write("*Generated by flight_dynamics_analysis.py - PhD Research Tool*\n")
        
        print(f"  💾 Saved: {report_file}")
        return report_file
    
    def run_full_analysis(self):
        """Execute complete flight dynamics analysis."""
        print("\n" + "="*80)
        print("🚁 FLIGHT DYNAMICS ANALYSIS - PhD Research Tool")
        print("="*80 + "\n")
        
        self.extract_data()
        
        imu_noise = self.analyze_imu_noise()
        altitude_metrics = self.analyze_altitude_hold()
        self.generate_bode_plot()
        report_file = self.generate_report(imu_noise, altitude_metrics)
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n📁 Output directory: {self.output_dir}")
        print(f"📄 Report: {report_file}\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze PX4 flight dynamics from .ulg telemetry logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python flight_dynamics_analysis.py ~/px4_logs/log_001.ulg
  python flight_dynamics_analysis.py /path/to/hover_test.ulg
        """
    )
    
    parser.add_argument('log_file', type=str, help='Path to PX4 .ulg log file')
    
    args = parser.parse_args()
    
    try:
        analyzer = FlightDynamicsAnalyzer(args.log_file)
        analyzer.run_full_analysis()
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
