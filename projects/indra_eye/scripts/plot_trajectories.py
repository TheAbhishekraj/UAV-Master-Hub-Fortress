#!/usr/bin/env python3
"""
Indra-Eye: Trajectory Plotter for PhD Thesis

Plots GPS, VIO, SLAM, and Fused trajectories from ROS bag for thesis documentation.

Usage:
    python3 plot_trajectories.py --bag rosbag_file.bag --output thesis_figure.png
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
import sys

def plot_trajectories(bag_path, output_path):
    """Plot all trajectories from ROS bag"""
    
    # Storage options
    storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id='sqlite3')
    converter_options = rosbag2_py.ConverterOptions('', '')
    
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    
    # Data containers
    gps_path = {'x': [], 'y': [], 't': []}
    vio_path = {'x': [], 'y': [], 't': []}
    slam_path = {'x': [], 'y': [], 't': []}
    fused_path = {'x': [], 'y': [], 't': []}
    
    # Read messages
    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}
    
    print(f"Reading bag: {bag_path}")
    
    while reader.has_next():
        (topic, data, timestamp) = reader.read_next()
        
        msg_type = get_message(type_map[topic])
        msg = deserialize_message(data, msg_type)
        
        t = timestamp * 1e-9  # Convert to seconds
        
        if topic == '/visualization/gps_path':
            if len(msg.poses) > 0:
                gps_path['x'] = [p.pose.position.x for p in msg.poses]
                gps_path['y'] = [p.pose.position.y for p in msg.poses]
                gps_path['t'] = [t] * len(msg.poses)
        
        elif topic == '/visualization/vio_path':
            if len(msg.poses) > 0:
                vio_path['x'] = [p.pose.position.x for p in msg.poses]
                vio_path['y'] = [p.pose.position.y for p in msg.poses]
                vio_path['t'] = [t] * len(msg.poses)
        
        elif topic == '/visualization/slam_path':
            if len(msg.poses) > 0:
                slam_path['x'] = [p.pose.position.x for p in msg.poses]
                slam_path['y'] = [p.pose.position.y for p in msg.poses]
                slam_path['t'] = [t] * len(msg.poses)
        
        elif topic == '/visualization/fused_path':
            if len(msg.poses) > 0:
                fused_path['x'] = [p.pose.position.x for p in msg.poses]
                fused_path['y'] = [p.pose.position.y for p in msg.poses]
                fused_path['t'] = [t] * len(msg.poses)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Plot trajectories
    if len(gps_path['x']) > 0:
        ax.plot(gps_path['x'], gps_path['y'], 'r-', linewidth=2, label='GPS (Raw)', alpha=0.7)
    
    if len(vio_path['x']) > 0:
        ax.plot(vio_path['x'], vio_path['y'], 'b-', linewidth=2, label='VIO', alpha=0.7)
    
    if len(slam_path['x']) > 0:
        ax.plot(slam_path['x'], slam_path['y'], 'c-', linewidth=2, label='SLAM', alpha=0.7)
    
    if len(fused_path['x']) > 0:
        ax.plot(fused_path['x'], fused_path['y'], 'g-', linewidth=3, label='Indra-Eye (Fused)', alpha=0.9)
    
    # Mark start and end
    if len(fused_path['x']) > 0:
        ax.plot(fused_path['x'][0], fused_path['y'][0], 'go', markersize=15, label='Start', zorder=10)
        ax.plot(fused_path['x'][-1], fused_path['y'][-1], 'rs', markersize=15, label='End', zorder=10)
    
    # Formatting
    ax.set_xlabel('East (m)', fontsize=14)
    ax.set_ylabel('North (m)', fontsize=14)
    ax.set_title('Indra-Eye Multi-Sensor Trajectory Comparison', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='box')
    
    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Plot saved to: {output_path}")
    
    # Calculate statistics
    if len(fused_path['x']) > 0 and len(gps_path['x']) > 0:
        gps_dist = np.sqrt((gps_path['x'][-1] - gps_path['x'][0])**2 + 
                          (gps_path['y'][-1] - gps_path['y'][0])**2)
        fused_dist = np.sqrt((fused_path['x'][-1] - fused_path['x'][0])**2 + 
                            (fused_path['y'][-1] - fused_path['y'][0])**2)
        
        print(f"\n📊 Statistics:")
        print(f"  GPS distance traveled: {gps_dist:.2f} m")
        print(f"  Fused distance traveled: {fused_dist:.2f} m")
        print(f"  Difference: {abs(gps_dist - fused_dist):.2f} m ({abs(gps_dist - fused_dist)/gps_dist*100:.2f}%)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot Indra-Eye trajectories from ROS bag')
    parser.add_argument('--bag', required=True, help='Path to ROS bag file')
    parser.add_argument('--output', default='trajectory_plot.png', help='Output image path')
    
    args = parser.parse_args()
    
    try:
        plot_trajectories(args.bag, args.output)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
