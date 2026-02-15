/******************************************************************************
 * Indra-Eye: Path Aggregator Node
 *
 * Converts point measurements (GPS, VIO, SLAM, Fused) to nav_msgs/Path
 * for RViz visualization with color-coded trajectories.
 *
 * Author: Indra-Eye Development Team
 * License: MIT
 *****************************************************************************/

#include <deque>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <nav_msgs/msg/path.hpp>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>

class PathAggregatorNode : public rclcpp::Node {
public:
  PathAggregatorNode() : Node("path_aggregator_node") {
    // Parameters
    this->declare_parameter("max_path_length", 1000);
    this->declare_parameter("publish_rate_hz", 10.0);
    this->declare_parameter("home_latitude", 34.1526);
    this->declare_parameter("home_longitude", 77.5771);
    this->declare_parameter("home_altitude", 3500.0);

    max_path_length_ = this->get_parameter("max_path_length").as_int();
    double publish_rate = this->get_parameter("publish_rate_hz").as_double();
    home_lat_ = this->get_parameter("home_latitude").as_double();
    home_lon_ = this->get_parameter("home_longitude").as_double();
    home_alt_ = this->get_parameter("home_altitude").as_double();

    // Subscribers
    gnss_sub_ = this->create_subscription<sensor_msgs::msg::NavSatFix>(
        "/px4/gnss", 10,
        std::bind(&PathAggregatorNode::gnssCallback, this,
                  std::placeholders::_1));

    vio_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
        "/camera/stereo/odom", 30,
        std::bind(&PathAggregatorNode::vioCallback, this,
                  std::placeholders::_1));

    slam_sub_ = this->create_subscription<
        geometry_msgs::msg::PoseWithCovarianceStamped>(
        "/lidar/slam/pose", 10,
        std::bind(&PathAggregatorNode::slamCallback, this,
                  std::placeholders::_1));

    fused_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
        "/indra_eye/fused_odom", 100,
        std::bind(&PathAggregatorNode::fusedCallback, this,
                  std::placeholders::_1));

    // Publishers
    gps_path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
        "/visualization/gps_path", 10);

    vio_path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
        "/visualization/vio_path", 10);

    slam_path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
        "/visualization/slam_path", 10);

    fused_path_pub_ = this->create_publisher<nav_msgs::msg::Path>(
        "/visualization/fused_path", 10);

    // Timer for publishing paths
    publish_timer_ = this->create_wall_timer(
        std::chrono::milliseconds(static_cast<int>(1000.0 / publish_rate)),
        std::bind(&PathAggregatorNode::publishPaths, this));

    RCLCPP_INFO(this->get_logger(), "Path Aggregator Node initialized");
    RCLCPP_INFO(this->get_logger(), "Max path length: %d points",
                max_path_length_);
  }

private:
  void gnssCallback(const sensor_msgs::msg::NavSatFix::SharedPtr msg) {
    // Convert lat/lon to local ENU
    double east, north, up;
    latLonToENU(msg->latitude, msg->longitude, msg->altitude, east, north, up);

    auto pose = geometry_msgs::msg::PoseStamped();
    pose.header = msg->header;
    pose.header.frame_id = "map";
    pose.pose.position.x = east;
    pose.pose.position.y = north;
    pose.pose.position.z = up;
    pose.pose.orientation.w = 1.0; // No orientation from GPS

    addToPath(gps_path_, pose);
  }

  void vioCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
    auto pose = geometry_msgs::msg::PoseStamped();
    pose.header = msg->header;
    pose.header.frame_id = "map";
    pose.pose = msg->pose.pose;

    addToPath(vio_path_, pose);
  }

  void slamCallback(
      const geometry_msgs::msg::PoseWithCovarianceStamped::SharedPtr msg) {
    auto pose = geometry_msgs::msg::PoseStamped();
    pose.header = msg->header;
    pose.header.frame_id = "map";
    pose.pose = msg->pose.pose;

    addToPath(slam_path_, pose);
  }

  void fusedCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
    auto pose = geometry_msgs::msg::PoseStamped();
    pose.header = msg->header;
    pose.header.frame_id = "map";
    pose.pose = msg->pose.pose;

    addToPath(fused_path_, pose);
  }

  void addToPath(std::deque<geometry_msgs::msg::PoseStamped> &path,
                 const geometry_msgs::msg::PoseStamped &pose) {
    path.push_back(pose);

    // Maintain max length (circular buffer)
    if (static_cast<int>(path.size()) > max_path_length_) {
      path.pop_front();
    }
  }

  void publishPaths() {
    // Publish all paths
    publishPath(gps_path_pub_, gps_path_, "map");
    publishPath(vio_path_pub_, vio_path_, "map");
    publishPath(slam_path_pub_, slam_path_, "map");
    publishPath(fused_path_pub_, fused_path_, "map");
  }

  void
  publishPath(rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr pub,
              const std::deque<geometry_msgs::msg::PoseStamped> &path_deque,
              const std::string &frame_id) {
    if (path_deque.empty())
      return;

    auto path_msg = nav_msgs::msg::Path();
    path_msg.header.stamp = this->now();
    path_msg.header.frame_id = frame_id;

    // Convert deque to vector
    path_msg.poses.assign(path_deque.begin(), path_deque.end());

    pub->publish(path_msg);
  }

  void latLonToENU(double lat, double lon, double alt, double &east,
                   double &north, double &up) {
    // Simple local tangent plane approximation
    const double EARTH_RADIUS = 6378137.0; // meters

    double delta_lat = (lat - home_lat_) * M_PI / 180.0;
    double delta_lon = (lon - home_lon_) * M_PI / 180.0;

    north = delta_lat * EARTH_RADIUS;
    east = delta_lon * EARTH_RADIUS * std::cos(home_lat_ * M_PI / 180.0);
    up = alt - home_alt_;
  }

  // Member variables
  int max_path_length_;
  double home_lat_;
  double home_lon_;
  double home_alt_;

  std::deque<geometry_msgs::msg::PoseStamped> gps_path_;
  std::deque<geometry_msgs::msg::PoseStamped> vio_path_;
  std::deque<geometry_msgs::msg::PoseStamped> slam_path_;
  std::deque<geometry_msgs::msg::PoseStamped> fused_path_;

  // ROS subscribers
  rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr gnss_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr vio_sub_;
  rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr
      slam_sub_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr fused_sub_;

  // ROS publishers
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr gps_path_pub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr vio_path_pub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr slam_path_pub_;
  rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr fused_path_pub_;

  // Timers
  rclcpp::TimerBase::SharedPtr publish_timer_;
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<PathAggregatorNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
