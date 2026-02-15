/******************************************************************************
 * Indra-Eye: MAVROS Bridge Node
 *
 * Translates ES-EKF fused pose to MAVLink messages for QGroundControl display.
 * Broadcasts sensor health and spoofing alerts.
 *
 * Author: Indra-Eye Development Team
 * License: MIT
 *****************************************************************************/

#include <Eigen/Dense>
#include <cmath>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/twist_stamped.hpp>
#include <mavros_msgs/msg/state.hpp>
#include <mavros_msgs/srv/command_long.hpp>
#include <mavros_msgs/srv/set_mode.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>
#include <std_msgs/msg/bool.hpp>
#include <std_msgs/msg/string.hpp>

class MAVROSBridgeNode : public rclcpp::Node {
public:
  MAVROSBridgeNode() : Node("mavros_bridge_node") {
    // Parameters
    this->declare_parameter("home_latitude", 34.1526); // Leh, Ladakh
    this->declare_parameter("home_longitude", 77.5771);
    this->declare_parameter("home_altitude", 3500.0); // meters

    home_lat_ = this->get_parameter("home_latitude").as_double();
    home_lon_ = this->get_parameter("home_longitude").as_double();
    home_alt_ = this->get_parameter("home_altitude").as_double();

    // Subscribers (from Indra-Eye)
    fused_odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
        "/indra_eye/fused_odom", 100,
        std::bind(&MAVROSBridgeNode::fusedOdomCallback, this,
                  std::placeholders::_1));

    nav_mode_sub_ = this->create_subscription<std_msgs::msg::String>(
        "/indra_eye/navigation_mode", 10,
        std::bind(&MAVROSBridgeNode::navModeCallback, this,
                  std::placeholders::_1));

    spoofing_sub_ = this->create_subscription<std_msgs::msg::Bool>(
        "/indra_eye/spoofing_detected", 10,
        std::bind(&MAVROSBridgeNode::spoofingCallback, this,
                  std::placeholders::_1));

    // Publishers (to MAVROS → QGC)
    local_pose_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
        "/mavros/vision_pose/pose", 100);

    velocity_pub_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
        "/mavros/vision_pose/twist", 100);

    global_pos_pub_ = this->create_publisher<sensor_msgs::msg::NavSatFix>(
        "/mavros/global_position/global", 10);

    // Service clients for sending status text to QGC
    statustext_client_ = this->create_client<mavros_msgs::srv::CommandLong>(
        "/mavros/cmd/command");

    // Timer for periodic health broadcast
    health_timer_ = this->create_wall_timer(
        std::chrono::seconds(1),
        std::bind(&MAVROSBridgeNode::publishHealth, this));

    current_mode_ = "INITIALIZING";
    spoofing_active_ = false;

    RCLCPP_INFO(this->get_logger(), "MAVROS Bridge Node initialized");
    RCLCPP_INFO(this->get_logger(), "Home: %.6f, %.6f, %.1fm", home_lat_,
                home_lon_, home_alt_);
  }

private:
  void fusedOdomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
    // Convert ENU to NED for MAVLink
    auto local_pose = geometry_msgs::msg::PoseStamped();
    local_pose.header = msg->header;
    local_pose.header.frame_id = "map";

    // ENU to NED conversion
    // ENU: x=East, y=North, z=Up
    // NED: x=North, y=East, z=Down
    local_pose.pose.position.x = msg->pose.pose.position.y;  // North
    local_pose.pose.position.y = msg->pose.pose.position.x;  // East
    local_pose.pose.position.z = -msg->pose.pose.position.z; // Down

    // Orientation: ENU to NED quaternion conversion
    // q_NED = q_ENU * q_rotation(90° around Z) * q_rotation(180° around X)
    Eigen::Quaterniond q_enu(
        msg->pose.pose.orientation.w, msg->pose.pose.orientation.x,
        msg->pose.pose.orientation.y, msg->pose.pose.orientation.z);

    // Simplified: just swap and negate appropriately
    local_pose.pose.orientation.w = q_enu.w();
    local_pose.pose.orientation.x = q_enu.y();
    local_pose.pose.orientation.y = q_enu.x();
    local_pose.pose.orientation.z = -q_enu.z();

    local_pose_pub_->publish(local_pose);

    // Velocity (also ENU to NED)
    auto velocity = geometry_msgs::msg::TwistStamped();
    velocity.header = msg->header;
    velocity.twist.linear.x = msg->twist.twist.linear.y;  // North
    velocity.twist.linear.y = msg->twist.twist.linear.x;  // East
    velocity.twist.linear.z = -msg->twist.twist.linear.z; // Down

    velocity_pub_->publish(velocity);

    // Convert local ENU to global lat/lon/alt for QGC map display
    publishGlobalPosition(msg->pose.pose.position.x, msg->pose.pose.position.y,
                          msg->pose.pose.position.z);
  }

  void navModeCallback(const std_msgs::msg::String::SharedPtr msg) {
    std::string previous_mode = current_mode_;
    current_mode_ = msg->data;

    if (current_mode_ != previous_mode) {
      RCLCPP_INFO(this->get_logger(), "Navigation mode: %s",
                  current_mode_.c_str());

      // Send mode change to QGC
      std::string status_msg;
      if (current_mode_ == "GNSS_HEALTHY") {
        status_msg = "✓ GNSS Mode - High Accuracy";
      } else if (current_mode_ == "VIO_FALLBACK") {
        status_msg = "⚠ VIO Mode - GPS Denied";
      } else if (current_mode_ == "SLAM_MODE") {
        status_msg = "⚠ SLAM Mode - Extended GPS Outage";
      } else if (current_mode_ == "EMERGENCY_DEAD_RECKONING") {
        status_msg = "🚨 EMERGENCY - Dead Reckoning Only";
      }

      sendStatusText(status_msg, getSeverityLevel(current_mode_));
    }
  }

  void spoofingCallback(const std_msgs::msg::Bool::SharedPtr msg) {
    if (msg->data && !spoofing_active_) {
      // Spoofing just detected
      spoofing_active_ = true;
      RCLCPP_ERROR(this->get_logger(), "GPS SPOOFING DETECTED!");

      sendStatusText("🚨 GPS SPOOFING DETECTED - SWITCHED TO VIO",
                     2); // CRITICAL

      // Log event with timestamp
      auto now = this->now();
      RCLCPP_ERROR(this->get_logger(), "Spoofing event logged at %ld.%09ld",
                   now.seconds(), now.nanoseconds());
    } else if (!msg->data && spoofing_active_) {
      // Spoofing cleared
      spoofing_active_ = false;
      RCLCPP_INFO(this->get_logger(), "GPS spoofing cleared");
      sendStatusText("✓ GPS Spoofing Cleared - Monitoring", 6); // INFO
    }
  }

  void publishGlobalPosition(double east, double north, double up) {
    // Simple local tangent plane approximation
    // For production, use proper geodetic conversion (e.g., GeographicLib)

    const double EARTH_RADIUS = 6378137.0; // meters

    double delta_lat = north / EARTH_RADIUS * (180.0 / M_PI);
    double delta_lon = east /
                       (EARTH_RADIUS * std::cos(home_lat_ * M_PI / 180.0)) *
                       (180.0 / M_PI);

    auto global_pos = sensor_msgs::msg::NavSatFix();
    global_pos.header.stamp = this->now();
    global_pos.header.frame_id = "map";

    global_pos.latitude = home_lat_ + delta_lat;
    global_pos.longitude = home_lon_ + delta_lon;
    global_pos.altitude = home_alt_ + up;

    global_pos.status.status = sensor_msgs::msg::NavSatStatus::STATUS_FIX;
    global_pos.status.service = sensor_msgs::msg::NavSatStatus::SERVICE_GPS;

    global_pos_pub_->publish(global_pos);
  }

  void publishHealth() {
    // Broadcast sensor health status
    std::string health_msg = "Indra-Eye: " + current_mode_;

    if (spoofing_active_) {
      health_msg += " | SPOOFING ACTIVE";
    }

    // Send as low-priority info message (don't spam QGC)
    // Only send if mode changed or spoofing active
    if (spoofing_active_) {
      sendStatusText(health_msg, 6); // INFO
    }
  }

  void sendStatusText(const std::string &text, uint8_t severity) {
    // MAVLink STATUSTEXT via COMMAND_LONG service
    // MAV_CMD_DO_SET_MODE (176) can be used, but we'll use logging

    // For now, just log to console (QGC integration requires mavros_extras)
    switch (severity) {
    case 0: // EMERGENCY
    case 1: // ALERT
    case 2: // CRITICAL
      RCLCPP_ERROR(this->get_logger(), "[QGC] %s", text.c_str());
      break;
    case 3: // ERROR
    case 4: // WARNING
      RCLCPP_WARN(this->get_logger(), "[QGC] %s", text.c_str());
      break;
    default: // NOTICE, INFO, DEBUG
      RCLCPP_INFO(this->get_logger(), "[QGC] %s", text.c_str());
      break;
    }

    // TODO: Implement actual MAVLink STATUSTEXT message
    // Requires mavros_extras/statustext plugin
  }

  uint8_t getSeverityLevel(const std::string &mode) {
    if (mode == "EMERGENCY_DEAD_RECKONING")
      return 2; // CRITICAL
    if (mode == "SLAM_MODE")
      return 4; // WARNING
    if (mode == "VIO_FALLBACK")
      return 4; // WARNING
    return 6;   // INFO
  }

  // Member variables
  double home_lat_;
  double home_lon_;
  double home_alt_;

  std::string current_mode_;
  bool spoofing_active_;

  // ROS subscribers
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr fused_odom_sub_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr nav_mode_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr spoofing_sub_;

  // ROS publishers
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr local_pose_pub_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr velocity_pub_;
  rclcpp::Publisher<sensor_msgs::msg::NavSatFix>::SharedPtr global_pos_pub_;

  // Service clients
  rclcpp::Client<mavros_msgs::srv::CommandLong>::SharedPtr statustext_client_;

  // Timers
  rclcpp::TimerBase::SharedPtr health_timer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MAVROSBridgeNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
