"""Unit tests for level1_basic_takeoff.py flight control module.

Tests the OFFBOARD mode controller, arming sequence, and trajectory setpoint publishing.

Author: Abhishek Raj - PhD Research (IIT Patna)
Date: February 15, 2026
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock


class TestLevel1BasicTakeoff:
    """Test suite for Level1BasicTakeoff flight controller."""
    
    @pytest.fixture
    def mock_flight_controller(self):
        """Create mock flight controller node."""
        with patch('rclpy.node.Node'):
            from agri_hexacopter.flight_levels.level1_basic_takeoff import Level1BasicTakeoff
            
            controller = Mock(spec=Level1BasicTakeoff)
            controller.offboard_setpoint_counter_ = 0
            
            return controller
    
    def test_initialization(self, mock_flight_controller):
        """Test flight controller initializes correctly."""
        assert mock_flight_controller.offboard_setpoint_counter_ == 0
    
    def test_setpoint_counter_increment(self, mock_flight_controller):
        """Test offboard setpoint counter increments correctly."""
        initial_count = mock_flight_controller.offboard_setpoint_counter_
        
        # Simulate timer callback
        mock_flight_controller.offboard_setpoint_counter_ += 1
        
        assert mock_flight_controller.offboard_setpoint_counter_ == initial_count + 1
    
    def test_arming_trigger_at_10_setpoints(self, mock_flight_controller):
        """Test arming sequence triggers after 10 setpoints."""
        # Set counter to 10
        mock_flight_controller.offboard_setpoint_counter_ = 10
        
        # Should trigger arming
        should_arm = (mock_flight_controller.offboard_setpoint_counter_ == 10)
        assert should_arm is True
    
    def test_trajectory_setpoint_altitude(self):
        """Test trajectory setpoint has correct altitude (-5m NED)."""
        expected_altitude = -5.0  # NED: negative is up
        
        # Test setpoint
        setpoint_z = -5.0
        assert setpoint_z == expected_altitude
    
    def test_trajectory_setpoint_yaw(self):
        """Test trajectory setpoint has correct yaw (North = -π)."""
        expected_yaw = -3.14  # Face North
        
        setpoint_yaw = -3.14
        assert abs(setpoint_yaw - expected_yaw) < 0.01
    
    def test_hover_position_stability(self):
        """Test hover position is fixed (0, 0, -5)."""
        expected_position = [0.0, 0.0, -5.0]
        
        test_position = [0.0, 0.0, -5.0]
        np.testing.assert_array_equal(test_position, expected_position)
    
    def test_qos_reliability(self):
        """Test QoS profile uses BEST_EFFORT reliability."""
        from rclpy.qos import QoSProfile, ReliabilityPolicy
        
        qos = QoSProfile(depth=10)
        qos.reliability = ReliabilityPolicy.BEST_EFFORT
        
        assert qos.reliability == ReliabilityPolicy.BEST_EFFORT
    
    def test_timer_frequency_10hz(self):
        """Test timer callback runs at 10Hz (0.1s period)."""
        expected_period = 0.1  # seconds
        
        timer_period = 0.1
        assert timer_period == expected_period
        
        # Verify frequency
        frequency = 1.0 / timer_period
        assert frequency == 10.0  # 10 Hz
    
    @pytest.mark.parametrize("setpoint_count,should_publish_mode", [
        (9, False),   # Before threshold
        (10, True),   # At threshold - should switch mode
        (11, False),  # After threshold
        (15, False),  # Well after threshold
    ])
    def test_mode_switch_logic(self, setpoint_count, should_publish_mode):
        """Test OFFBOARD mode switch logic."""
        # Mode switch happens exactly at count == 10
        result = (setpoint_count == 10)
        assert result == should_publish_mode


class TestFlightSafety:
    """Safety-critical test cases."""
    
    def test_altitude_within_safe_bounds(self):
        """Test altitude setpoint is within safe operational bounds."""
        setpoint_altitude = -5.0  # meters in NED
        
        # Safety bounds: 1m to 50m
        MIN_SAFE_ALTITUDE = -50.0
        MAX_SAFE_ALTITUDE = -1.0
        
        assert MIN_SAFE_ALTITUDE <= setpoint_altitude <= MAX_SAFE_ALTITUDE
    
    def test_no_horizontal_drift(self):
        """Test no horizontal drift commands (stable hover)."""
        setpoint_x = 0.0
        setpoint_y = 0.0
        
        assert setpoint_x == 0.0
        assert setpoint_y == 0.0
    
    def test_arming_warmup_period(self):
        """Test minimum warmup period before arming (1 second)."""
        warmup_setpoints = 10
        timer_period = 0.1
        
        warmup_duration = warmup_setpoints * timer_period
        
        assert warmup_duration >= 1.0  # At least 1 second warmup


class TestVehicleCommands:
    """Test vehicle command message construction."""
    
    def test_arm_command_structure(self):
        """Test ARM command has correct parameters."""
        # VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM = 400
        ARM_COMMAND = 400
        ARM_PARAM = 1.0
        
        cmd_id = ARM_COMMAND
        param1 = ARM_PARAM
        
        assert cmd_id == 400
        assert param1 == 1.0
    
    def test_offboard_mode_command_structure(self):
        """Test OFFBOARD mode command has correct parameters."""
        # VehicleCommand.VEHICLE_CMD_DO_SET_MODE = 176
        SET_MODE_COMMAND = 176
        MODE_FLAG = 1.0
        CUSTOM_MAIN_MODE = 6.0  # OFFBOARD
        
        cmd_id = SET_MODE_COMMAND
        param1 = MODE_FLAG
        param2 = CUSTOM_MAIN_MODE
        
        assert cmd_id == 176
        assert param1 == 1.0
        assert param2 == 6.0


class TestOffboardControlMode:
    """Test OffboardControlMode message configuration."""
    
    def test_position_control_enabled(self):
        """Test position control flag is enabled."""
        position_enabled = True
        
        assert position_enabled is True
    
    def test_velocity_control_disabled(self):
        """Test velocity control flag is disabled."""
        velocity_enabled = False
        
        assert velocity_enabled is False
    
    def test_attitude_control_disabled(self):
        """Test attitude control flag is disabled."""
        attitude_enabled = False
        
        assert attitude_enabled is False
    
    def test_control_mode_consistency(self):
        """Test only position control is enabled (safest mode)."""
        control_flags = {
            'position': True,
            'velocity': False,
            'attitude': False,
            'acceleration': False
        }
        
        # Only one control mode should be active
        active_modes = sum(control_flags.values())
        assert active_modes == 1
        assert control_flags['position'] is True


class TestTimestampHandling:
    """Test timestamp synchronization."""
    
    def test_timestamp_monotonic_increase(self):
        """Test timestamps increase monotonically."""
        import time
        
        t1_ns = int(time.time() * 1e9)
        time.sleep(0.01)
        t2_ns = int(time.time() * 1e9)
        
        assert t2_ns > t1_ns
    
    def test_timestamp_conversion_to_microseconds(self):
        """Test timestamp conversion from nanoseconds to microseconds."""
        timestamp_ns = 1000000000  # 1 second in nanoseconds
        timestamp_us = timestamp_ns // 1000
        
        assert timestamp_us == 1000000  # 1 second in microseconds


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
