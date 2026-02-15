/******************************************************************************
 * Indra-Eye: Resilient UAV Positioning System
 * Anti-Jamming Supervisor Node
 * 
 * This node monitors sensor health and detects GNSS spoofing/jamming using
 * Mahalanobis distance test. Implements automatic failover logic.
 * 
 * Author: Indra-Eye Development Team
 * License: MIT
 *****************************************************************************/

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <std_msgs/msg/string.hpp>
#include <std_msgs/msg/bool.hpp>
#include <Eigen/Dense>
#include <cmath>

using Eigen::Vector3d;
using Eigen::Matrix3d;

enum class NavigationMode {
    GNSS_HEALTHY,
    VIO_FALLBACK,
    SLAM_MODE,
    EMERGENCY_DEAD_RECKONING
};

class SupervisorNode : public rclcpp::Node {
public:
    SupervisorNode() : Node("supervisor_node") {
        // Parameters
        this->declare_parameter("mahalanobis_threshold", 9.21);  // χ² for 3 DOF at 95% confidence
        this->declare_parameter("spoofing_detection_window", 2.0);  // seconds
        this->declare_parameter("gnss_timeout", 5.0);  // seconds
        
        mahalanobis_threshold_ = this->get_parameter("mahalanobis_threshold").as_double();
        spoofing_window_ = this->get_parameter("spoofing_detection_window").as_double();
        gnss_timeout_ = this->get_parameter("gnss_timeout").as_double();
        
        // Subscribers
        gnss_sub_ = this->create_subscription<sensor_msgs::msg::NavSatFix>(
            "/px4/gnss", 10,
            std::bind(&SupervisorNode::gnssCallback, this, std::placeholders::_1));
        
        vio_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/camera/stereo/odom", 30,
            std::bind(&SupervisorNode::vioCallback, this, std::placeholders::_1));
        
        ekf_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/indra_eye/fused_odom", 100,
            std::bind(&SupervisorNode::ekfCallback, this, std::placeholders::_1));
        
        // Publishers
        mode_pub_ = this->create_publisher<std_msgs::msg::String>(
            "/indra_eye/navigation_mode", 10);
        
        spoofing_alert_pub_ = this->create_publisher<std_msgs::msg::Bool>(
            "/indra_eye/spoofing_detected", 10);
        
        // Timer for monitoring
        monitor_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&SupervisorNode::monitorSensors, this));
        
        current_mode_ = NavigationMode::GNSS_HEALTHY;
        gnss_available_ = false;
        vio_available_ = false;
        spoofing_detected_ = false;
        
        last_gnss_time_ = this->now();
        last_vio_time_ = this->now();
        
        RCLCPP_INFO(this->get_logger(), "Supervisor Node initialized");
    }

private:
    void gnssCallback(const sensor_msgs::msg::NavSatFix::SharedPtr msg) {
        last_gnss_time_ = this->now();
        gnss_available_ = true;
        
        // Convert to ENU (simplified)
        gnss_position_ = Vector3d(
            msg->longitude * 111320.0 * std::cos(msg->latitude * M_PI / 180.0),
            msg->latitude * 111320.0,
            msg->altitude
        );
        
        gnss_covariance_ = Matrix3d::Zero();
        gnss_covariance_(0, 0) = msg->position_covariance[0];
        gnss_covariance_(1, 1) = msg->position_covariance[4];
        gnss_covariance_(2, 2) = msg->position_covariance[8];
    }
    
    void vioCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        last_vio_time_ = this->now();
        vio_available_ = true;
        
        vio_position_ = Vector3d(
            msg->pose.pose.position.x,
            msg->pose.pose.position.y,
            msg->pose.pose.position.z
        );
        
        vio_covariance_ = Matrix3d::Zero();
        vio_covariance_(0, 0) = msg->pose.covariance[0];
        vio_covariance_(1, 1) = msg->pose.covariance[7];
        vio_covariance_(2, 2) = msg->pose.covariance[14];
    }
    
    void ekfCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        ekf_position_ = Vector3d(
            msg->pose.pose.position.x,
            msg->pose.pose.position.y,
            msg->pose.pose.position.z
        );
    }
    
    void monitorSensors() {
        auto now = this->now();
        
        // Check GNSS timeout
        double gnss_age = (now - last_gnss_time_).seconds();
        if (gnss_age > gnss_timeout_) {
            gnss_available_ = false;
        }
        
        // Check VIO timeout
        double vio_age = (now - last_vio_time_).seconds();
        if (vio_age > 1.0) {  // VIO should update at 30Hz
            vio_available_ = false;
        }
        
        // Spoofing detection using Mahalanobis distance
        if (gnss_available_ && vio_available_) {
            double mahalanobis_dist = computeMahalanobisDistance(
                gnss_position_, vio_position_, 
                gnss_covariance_ + vio_covariance_
            );
            
            if (mahalanobis_dist > mahalanobis_threshold_) {
                if (!spoofing_detected_) {
                    spoofing_start_time_ = now;
                    spoofing_detected_ = true;
                }
                
                // Confirm spoofing if persists for window duration
                double spoofing_duration = (now - spoofing_start_time_).seconds();
                if (spoofing_duration > spoofing_window_) {
                    handleSpoofingDetected();
                }
            } else {
                spoofing_detected_ = false;
            }
        }
        
        // State machine for mode transitions
        updateNavigationMode();
        
        // Publish current mode
        publishMode();
    }
    
    double computeMahalanobisDistance(const Vector3d& z1, const Vector3d& z2, 
                                     const Matrix3d& S) {
        Vector3d innovation = z1 - z2;
        
        // Mahalanobis distance: d² = (z1 - z2)^T * S^(-1) * (z1 - z2)
        double dist_squared = innovation.transpose() * S.inverse() * innovation;
        
        return dist_squared;
    }
    
    void handleSpoofingDetected() {
        RCLCPP_ERROR(this->get_logger(), 
                    "GNSS SPOOFING DETECTED! Mahalanobis distance exceeded threshold. "
                    "Switching to VIO/SLAM mode.");
        
        auto alert_msg = std_msgs::msg::Bool();
        alert_msg.data = true;
        spoofing_alert_pub_->publish(alert_msg);
        
        // Force mode change
        current_mode_ = NavigationMode::VIO_FALLBACK;
    }
    
    void updateNavigationMode() {
        NavigationMode previous_mode = current_mode_;
        
        switch (current_mode_) {
            case NavigationMode::GNSS_HEALTHY:
                if (spoofing_detected_ || !gnss_available_) {
                    if (vio_available_) {
                        current_mode_ = NavigationMode::VIO_FALLBACK;
                    } else {
                        current_mode_ = NavigationMode::SLAM_MODE;
                    }
                }
                break;
                
            case NavigationMode::VIO_FALLBACK:
                if (gnss_available_ && !spoofing_detected_) {
                    // Recovery to GNSS
                    current_mode_ = NavigationMode::GNSS_HEALTHY;
                } else if (!vio_available_) {
                    current_mode_ = NavigationMode::SLAM_MODE;
                }
                break;
                
            case NavigationMode::SLAM_MODE:
                if (gnss_available_ && !spoofing_detected_) {
                    current_mode_ = NavigationMode::GNSS_HEALTHY;
                } else if (vio_available_) {
                    current_mode_ = NavigationMode::VIO_FALLBACK;
                }
                break;
                
            case NavigationMode::EMERGENCY_DEAD_RECKONING:
                // Try to recover
                if (gnss_available_ && !spoofing_detected_) {
                    current_mode_ = NavigationMode::GNSS_HEALTHY;
                } else if (vio_available_) {
                    current_mode_ = NavigationMode::VIO_FALLBACK;
                }
                break;
        }
        
        // Log mode transitions
        if (current_mode_ != previous_mode) {
            RCLCPP_WARN(this->get_logger(), "Navigation mode changed: %s -> %s",
                       modeToString(previous_mode).c_str(),
                       modeToString(current_mode_).c_str());
        }
    }
    
    void publishMode() {
        auto mode_msg = std_msgs::msg::String();
        mode_msg.data = modeToString(current_mode_);
        mode_pub_->publish(mode_msg);
    }
    
    std::string modeToString(NavigationMode mode) {
        switch (mode) {
            case NavigationMode::GNSS_HEALTHY:
                return "GNSS_HEALTHY";
            case NavigationMode::VIO_FALLBACK:
                return "VIO_FALLBACK";
            case NavigationMode::SLAM_MODE:
                return "SLAM_MODE";
            case NavigationMode::EMERGENCY_DEAD_RECKONING:
                return "EMERGENCY_DEAD_RECKONING";
            default:
                return "UNKNOWN";
        }
    }
    
    // Member variables
    NavigationMode current_mode_;
    bool gnss_available_;
    bool vio_available_;
    bool spoofing_detected_;
    
    double mahalanobis_threshold_;
    double spoofing_window_;
    double gnss_timeout_;
    
    Vector3d gnss_position_;
    Vector3d vio_position_;
    Vector3d ekf_position_;
    
    Matrix3d gnss_covariance_;
    Matrix3d vio_covariance_;
    
    rclcpp::Time last_gnss_time_;
    rclcpp::Time last_vio_time_;
    rclcpp::Time spoofing_start_time_;
    
    // ROS interfaces
    rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr gnss_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr vio_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr ekf_sub_;
    
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr mode_pub_;
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr spoofing_alert_pub_;
    
    rclcpp::TimerBase::SharedPtr monitor_timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<SupervisorNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
