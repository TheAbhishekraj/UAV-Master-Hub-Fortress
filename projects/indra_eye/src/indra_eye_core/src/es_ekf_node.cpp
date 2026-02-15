/******************************************************************************
 * Indra-Eye: Resilient UAV Positioning System
 * ES-EKF ROS 2 Node Implementation
 * 
 * This node implements the Error-State Extended Kalman Filter for multi-sensor
 * fusion (GNSS + IMU + VIO + LiDAR SLAM).
 * 
 * Subscriptions:
 *   - /px4/imu (400Hz): High-rate IMU data
 *   - /px4/gnss (10Hz): GNSS position/velocity
 *   - /camera/stereo/odom (30Hz): Visual odometry
 *   - /lidar/slam/pose (10Hz): LiDAR SLAM pose
 * 
 * Publications:
 *   - /indra_eye/fused_pose (100Hz): Fused position estimate
 *   - /indra_eye/covariance (10Hz): Uncertainty ellipsoid
 *   - /indra_eye/diagnostics (1Hz): Filter health status
 * 
 * Author: Indra-Eye Development Team
 * License: MIT
 *****************************************************************************/

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/pose_with_covariance_stamped.hpp>
#include <diagnostic_msgs/msg/diagnostic_status.hpp>
#include <std_msgs/msg/bool.hpp>

#include "indra_eye_core/ekf_math.hpp"
#include <deque>
#include <memory>

using namespace indra_eye;

class ESEKFNode : public rclcpp::Node {
public:
    ESEKFNode() : Node("es_ekf_node") {
        // Initialize state
        state_ = std::make_shared<ESEKFState>();
        noise_params_ = IMUNoiseParams();
        
        // Declare parameters
        this->declare_parameter("use_gnss", true);
        this->declare_parameter("use_vio", true);
        this->declare_parameter("use_slam", true);
        this->declare_parameter("publish_rate_hz", 100.0);
        
        // Subscribers
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/px4/imu", rclcpp::SensorDataQoS(),
            std::bind(&ESEKFNode::imuCallback, this, std::placeholders::_1));
        
        gnss_sub_ = this->create_subscription<sensor_msgs::msg::NavSatFix>(
            "/px4/gnss", 10,
            std::bind(&ESEKFNode::gnssCallback, this, std::placeholders::_1));
        
        vio_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "/camera/stereo/odom", 30,
            std::bind(&ESEKFNode::vioCallback, this, std::placeholders::_1));
        
        slam_sub_ = this->create_subscription<geometry_msgs::msg::PoseWithCovarianceStamped>(
            "/lidar/slam/pose", 10,
            std::bind(&ESEKFNode::slamCallback, this, std::placeholders::_1));
        
        gps_denial_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            "/indra_eye/simulate_gps_denial", 10,
            std::bind(&ESEKFNode::gpsDenialCallback, this, std::placeholders::_1));
        
        // Publishers
        pose_pub_ = this->create_publisher<geometry_msgs::msg::PoseWithCovarianceStamped>(
            "/indra_eye/fused_pose", 100);
        
        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>(
            "/indra_eye/fused_odom", 100);
        
        diagnostics_pub_ = this->create_publisher<diagnostic_msgs::msg::DiagnosticStatus>(
            "/indra_eye/diagnostics", 1);
        
        // Timer for diagnostics
        diagnostics_timer_ = this->create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&ESEKFNode::publishDiagnostics, this));
        
        RCLCPP_INFO(this->get_logger(), "ES-EKF Node initialized");
        
        initialized_ = false;
        gps_denied_ = false;
        imu_count_ = 0;
        gnss_count_ = 0;
        vio_count_ = 0;
        slam_count_ = 0;
    }

private:
    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg) {
        imu_count_++;
        
        // Convert ROS message to internal format
        IMUMeasurement imu;
        imu.accel = Vector3d(msg->linear_acceleration.x,
                            msg->linear_acceleration.y,
                            msg->linear_acceleration.z);
        imu.gyro = Vector3d(msg->angular_velocity.x,
                           msg->angular_velocity.y,
                           msg->angular_velocity.z);
        imu.timestamp = msg->header.stamp.sec + msg->header.stamp.nanosec * 1e-9;
        
        if (!initialized_) {
            // Initialize state with first IMU measurement
            state_->timestamp = imu.timestamp;
            state_->accel_bias = Vector3d(0.0, 0.0, 0.0);
            state_->gyro_bias = Vector3d(0.0, 0.0, 0.0);
            
            // Initial orientation from gravity vector
            Vector3d gravity_dir = imu.accel.normalized();
            Vector3d z_body(0, 0, 1);
            
            // Simple initialization (assumes level flight)
            state_->orientation = Quaterniond::Identity();
            
            RCLCPP_INFO(this->get_logger(), "Filter initialized with IMU data");
            initialized_ = true;
            return;
        }
        
        // Prediction step (high-rate IMU propagation)
        double dt = imu.timestamp - state_->timestamp;
        if (dt > 0 && dt < 0.1) {  // Sanity check
            propagateNominalState(*state_, imu, dt);
            propagateErrorCovariance(*state_, imu.accel, noise_params_, dt);
        }
        
        // Publish fused pose at configured rate
        if (imu_count_ % 4 == 0) {  // 400Hz / 4 = 100Hz
            publishFusedPose();
        }
    }
    
    void gnssCallback(const sensor_msgs::msg::NavSatFix::SharedPtr msg) {
        if (!initialized_ || gps_denied_) return;
        
        gnss_count_++;
        
        // Convert lat/lon/alt to ENU (simplified - assumes local tangent plane)
        // In production, use proper geodetic conversion
        Vector3d gnss_position(
            msg->longitude * 111320.0 * std::cos(msg->latitude * M_PI / 180.0),
            msg->latitude * 111320.0,
            msg->altitude
        );
        
        // Measurement update (position only)
        updateWithPositionMeasurement(gnss_position, 
                                     Vector3d(msg->position_covariance[0],
                                             msg->position_covariance[4],
                                             msg->position_covariance[8]));
    }
    
    void vioCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        if (!initialized_) return;
        
        vio_count_++;
        
        // Extract position from VIO
        Vector3d vio_position(msg->pose.pose.position.x,
                             msg->pose.pose.position.y,
                             msg->pose.pose.position.z);
        
        // Extract covariance
        Vector3d vio_cov(msg->pose.covariance[0],
                        msg->pose.covariance[7],
                        msg->pose.covariance[14]);
        
        // Measurement update
        updateWithPositionMeasurement(vio_position, vio_cov);
    }
    
    void slamCallback(const geometry_msgs::msg::PoseWithCovarianceStamped::SharedPtr msg) {
        if (!initialized_) return;
        
        slam_count_++;
        
        // Extract position from SLAM
        Vector3d slam_position(msg->pose.pose.position.x,
                              msg->pose.pose.position.y,
                              msg->pose.pose.position.z);
        
        // Extract covariance
        Vector3d slam_cov(msg->pose.covariance[0],
                         msg->pose.covariance[7],
                         msg->pose.covariance[14]);
        
        // Measurement update
        updateWithPositionMeasurement(slam_position, slam_cov);
    }
    
    void gpsDenialCallback(const std_msgs::msg::Bool::SharedPtr msg) {
        gps_denied_ = msg->data;
        if (gps_denied_) {
            RCLCPP_WARN(this->get_logger(), "GPS DENIED - Switching to VIO/SLAM mode");
        } else {
            RCLCPP_INFO(this->get_logger(), "GPS RESTORED - Resuming GNSS fusion");
        }
    }
    
    void updateWithPositionMeasurement(const Vector3d& measured_pos, 
                                      const Vector3d& measurement_variance) {
        // Measurement model: z = H * δx + v
        // For position measurement: H = [I_3x3, 0_3x12]
        
        Eigen::Matrix<double, 3, 15> H = Eigen::Matrix<double, 3, 15>::Zero();
        H.block<3, 3>(0, 0) = Matrix3d::Identity();
        
        // Measurement covariance
        Matrix3d R = measurement_variance.asDiagonal();
        
        // Innovation: z - h(x)
        Vector3d innovation = measured_pos - state_->position;
        
        // Innovation covariance: S = H * P * H^T + R
        Matrix3d S = H * state_->covariance * H.transpose() + R;
        
        // Kalman gain: K = P * H^T * S^(-1)
        Eigen::Matrix<double, 15, 3> K = state_->covariance * H.transpose() * S.inverse();
        
        // Error state update: δx = K * innovation
        state_->error_state = K * innovation;
        
        // Covariance update: P = (I - K * H) * P
        Matrix15d I_KH = Matrix15d::Identity() - K * H;
        state_->covariance = I_KH * state_->covariance * I_KH.transpose() + 
                            K * R * K.transpose();  // Joseph form for numerical stability
        
        // Inject error state into nominal state
        injectErrorState(*state_);
    }
    
    void publishFusedPose() {
        auto pose_msg = geometry_msgs::msg::PoseWithCovarianceStamped();
        pose_msg.header.stamp = this->now();
        pose_msg.header.frame_id = "enu";
        
        // Position
        pose_msg.pose.pose.position.x = state_->position(0);
        pose_msg.pose.pose.position.y = state_->position(1);
        pose_msg.pose.pose.position.z = state_->position(2);
        
        // Orientation
        pose_msg.pose.pose.orientation.w = state_->orientation.w();
        pose_msg.pose.pose.orientation.x = state_->orientation.x();
        pose_msg.pose.pose.orientation.y = state_->orientation.y();
        pose_msg.pose.pose.orientation.z = state_->orientation.z();
        
        // Covariance (position only, 6x6 matrix)
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                pose_msg.pose.covariance[i * 6 + j] = state_->covariance(i, j);
            }
        }
        
        pose_pub_->publish(pose_msg);
        
        // Also publish as Odometry
        auto odom_msg = nav_msgs::msg::Odometry();
        odom_msg.header = pose_msg.header;
        odom_msg.child_frame_id = "base_link";
        odom_msg.pose = pose_msg.pose;
        
        // Velocity
        odom_msg.twist.twist.linear.x = state_->velocity(0);
        odom_msg.twist.twist.linear.y = state_->velocity(1);
        odom_msg.twist.twist.linear.z = state_->velocity(2);
        
        odom_pub_->publish(odom_msg);
    }
    
    void publishDiagnostics() {
        auto diag_msg = diagnostic_msgs::msg::DiagnosticStatus();
        diag_msg.name = "ES-EKF Filter";
        diag_msg.hardware_id = "indra_eye_core";
        
        // Check filter health
        double pos_uncertainty = std::sqrt(state_->covariance(0, 0) + 
                                          state_->covariance(1, 1) + 
                                          state_->covariance(2, 2));
        
        if (!initialized_) {
            diag_msg.level = diagnostic_msgs::msg::DiagnosticStatus::WARN;
            diag_msg.message = "Filter not initialized";
        } else if (pos_uncertainty > 10.0) {
            diag_msg.level = diagnostic_msgs::msg::DiagnosticStatus::ERROR;
            diag_msg.message = "High position uncertainty";
        } else if (gps_denied_) {
            diag_msg.level = diagnostic_msgs::msg::DiagnosticStatus::WARN;
            diag_msg.message = "GPS denied - VIO/SLAM mode";
        } else {
            diag_msg.level = diagnostic_msgs::msg::DiagnosticStatus::OK;
            diag_msg.message = "Filter healthy";
        }
        
        // Add diagnostic values
        diagnostic_msgs::msg::KeyValue kv;
        
        kv.key = "IMU updates";
        kv.value = std::to_string(imu_count_);
        diag_msg.values.push_back(kv);
        
        kv.key = "GNSS updates";
        kv.value = std::to_string(gnss_count_);
        diag_msg.values.push_back(kv);
        
        kv.key = "VIO updates";
        kv.value = std::to_string(vio_count_);
        diag_msg.values.push_back(kv);
        
        kv.key = "SLAM updates";
        kv.value = std::to_string(slam_count_);
        diag_msg.values.push_back(kv);
        
        kv.key = "Position uncertainty (m)";
        kv.value = std::to_string(pos_uncertainty);
        diag_msg.values.push_back(kv);
        
        diagnostics_pub_->publish(diag_msg);
    }
    
    // Member variables
    std::shared_ptr<ESEKFState> state_;
    IMUNoiseParams noise_params_;
    bool initialized_;
    bool gps_denied_;
    
    uint64_t imu_count_;
    uint64_t gnss_count_;
    uint64_t vio_count_;
    uint64_t slam_count_;
    
    // ROS subscribers
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr gnss_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr vio_sub_;
    rclcpp::Subscription<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr slam_sub_;
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr gps_denial_sub_;
    
    // ROS publishers
    rclcpp::Publisher<geometry_msgs::msg::PoseWithCovarianceStamped>::SharedPtr pose_pub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    rclcpp::Publisher<diagnostic_msgs::msg::DiagnosticStatus>::SharedPtr diagnostics_pub_;
    
    // Timers
    rclcpp::TimerBase::SharedPtr diagnostics_timer_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<ESEKFNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
