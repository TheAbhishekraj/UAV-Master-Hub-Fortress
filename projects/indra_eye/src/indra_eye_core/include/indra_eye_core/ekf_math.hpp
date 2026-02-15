/******************************************************************************
 * Indra-Eye: Resilient UAV Positioning System
 * ES-EKF Mathematical Foundations
 * 
 * This header implements the Error-State Extended Kalman Filter mathematics
 * for a 15-state vector handling 400Hz IMU updates.
 * 
 * State Vector: [δp, δv, δθ, b_a, b_g]^T (15 dimensions)
 *   - δp (3D): Position error (East-North-Up frame)
 *   - δv (3D): Velocity error
 *   - δθ (3D): Attitude error (quaternion error representation)
 *   - b_a (3D): Accelerometer bias error
 *   - b_g (3D): Gyroscope bias error
 * 
 * Author: Indra-Eye Development Team
 * License: MIT
 *****************************************************************************/

#ifndef INDRA_EYE_CORE_EKF_MATH_HPP
#define INDRA_EYE_CORE_EKF_MATH_HPP

#include <Eigen/Dense>
#include <Eigen/Geometry>
#include <cmath>

namespace indra_eye {

// Constants
constexpr double GRAVITY = 9.80665;           // m/s^2 (standard gravity)
constexpr double EARTH_ROTATION = 7.2921159e-5; // rad/s (Earth rotation rate)
constexpr double IMU_FREQ = 400.0;            // Hz (IMU update frequency)
constexpr double DT = 1.0 / IMU_FREQ;         // Time step (0.0025s)

// State dimensions
constexpr int STATE_DIM = 15;
constexpr int ERROR_STATE_DIM = 15;
constexpr int NOISE_DIM = 12;

// Eigen type aliases
using Vector3d = Eigen::Vector3d;
using Vector15d = Eigen::Matrix<double, 15, 1>;
using Matrix3d = Eigen::Matrix3d;
using Matrix15d = Eigen::Matrix<double, 15, 15>;
using Matrix15x12d = Eigen::Matrix<double, 15, 12>;
using Matrix12d = Eigen::Matrix<double, 12, 12>;
using Quaterniond = Eigen::Quaterniond;

/**
 * @brief ES-EKF State representation
 */
struct ESEKFState {
    // Nominal state (propagated at high rate)
    Vector3d position;        // Position in ENU frame [m]
    Vector3d velocity;        // Velocity in ENU frame [m/s]
    Quaterniond orientation;  // Orientation quaternion (body to ENU)
    Vector3d accel_bias;      // Accelerometer bias [m/s^2]
    Vector3d gyro_bias;       // Gyroscope bias [rad/s]
    
    // Error state (updated during correction)
    Vector15d error_state;    // Error state vector (all zeros after injection)
    Matrix15d covariance;     // Error state covariance matrix
    
    // Timestamp
    double timestamp;         // Timestamp [s]
    
    ESEKFState() {
        position.setZero();
        velocity.setZero();
        orientation = Quaterniond::Identity();
        accel_bias.setZero();
        gyro_bias.setZero();
        error_state.setZero();
        covariance = Matrix15d::Identity() * 0.01; // Initial uncertainty
        timestamp = 0.0;
    }
};

/**
 * @brief IMU measurement structure
 */
struct IMUMeasurement {
    Vector3d accel;      // Specific force [m/s^2]
    Vector3d gyro;       // Angular velocity [rad/s]
    double timestamp;    // Timestamp [s]
};

/**
 * @brief Noise parameters for IMU
 */
struct IMUNoiseParams {
    double accel_noise_density;      // Accelerometer noise density [m/s^2/√Hz]
    double gyro_noise_density;       // Gyroscope noise density [rad/s/√Hz]
    double accel_random_walk;        // Accelerometer bias random walk [m/s^3/√Hz]
    double gyro_random_walk;         // Gyroscope bias random walk [rad/s^2/√Hz]
    
    // Default values for MPU-9250 (typical tactical-grade IMU)
    IMUNoiseParams() 
        : accel_noise_density(0.002),     // 2 mg/√Hz
          gyro_noise_density(0.00015),    // 0.15 deg/s/√Hz
          accel_random_walk(0.0003),      // 300 μg/√Hz
          gyro_random_walk(0.000025) {}   // 0.0025 deg/s/√Hz
};

/**
 * @brief Skew-symmetric matrix from vector (for cross product)
 * 
 * For vector v = [v1, v2, v3]^T, returns:
 *     [  0  -v3   v2 ]
 *     [ v3    0  -v1 ]
 *     [-v2   v1    0 ]
 * 
 * Property: skew(v) * w = v × w (cross product)
 */
inline Matrix3d skewSymmetric(const Vector3d& v) {
    Matrix3d skew;
    skew <<     0, -v(2),  v(1),
             v(2),     0, -v(0),
            -v(1),  v(0),     0;
    return skew;
}

/**
 * @brief Compute rotation matrix from quaternion
 */
inline Matrix3d quaternionToRotationMatrix(const Quaterniond& q) {
    return q.toRotationMatrix();
}

/**
 * @brief Compute quaternion from rotation vector (axis-angle)
 * 
 * For small angles (θ < 0.1 rad), uses first-order approximation:
 *   q ≈ [1, θ/2]^T
 * 
 * For larger angles, uses exact Rodrigues formula:
 *   q = [cos(θ/2), sin(θ/2) * axis]^T
 */
inline Quaterniond rotationVectorToQuaternion(const Vector3d& rot_vec) {
    double angle = rot_vec.norm();
    
    if (angle < 1e-8) {
        // Small angle approximation
        return Quaterniond(1.0, 
                          0.5 * rot_vec(0), 
                          0.5 * rot_vec(1), 
                          0.5 * rot_vec(2));
    } else {
        // Exact formula
        Vector3d axis = rot_vec / angle;
        double half_angle = 0.5 * angle;
        return Quaterniond(std::cos(half_angle),
                          std::sin(half_angle) * axis(0),
                          std::sin(half_angle) * axis(1),
                          std::sin(half_angle) * axis(2));
    }
}

/**
 * @brief Compute Discrete-Time State Transition Matrix (Φ_k)
 * 
 * Continuous-time error dynamics:
 *   δẋ = F_x * δx + F_w * w
 * 
 * Where F_x is the error state Jacobian:
 *   F_x = [ 0    I    0       0       0     ]  (position)
 *         [ 0    0   -R*[a]×  -R      0     ]  (velocity)
 *         [ 0    0    0       0      -R     ]  (orientation)
 *         [ 0    0    0       0       0     ]  (accel bias)
 *         [ 0    0    0       0       0     ]  (gyro bias)
 * 
 * R: Rotation matrix from body to ENU frame
 * [a]×: Skew-symmetric matrix of specific force measurement
 * 
 * Discretization using matrix exponential approximation:
 *   Φ_k = exp(F_x * Δt) ≈ I + F_x*Δt + (F_x*Δt)²/2
 * 
 * For Δt = 0.0025s (400Hz), second-order approximation is sufficient.
 */
inline Matrix15d computeStateTransitionMatrix(
    const Quaterniond& orientation,
    const Vector3d& accel_measurement,
    double dt = DT) {
    
    Matrix15d Phi = Matrix15d::Identity();
    Matrix3d R = quaternionToRotationMatrix(orientation);
    Matrix3d accel_skew = skewSymmetric(accel_measurement);
    
    // First-order terms (F_x * Δt)
    Phi.block<3, 3>(0, 3) = Matrix3d::Identity() * dt;  // δp += δv * dt
    Phi.block<3, 3>(3, 6) = -R * accel_skew * dt;       // δv += -R*[a]× * δθ * dt
    Phi.block<3, 3>(3, 9) = -R * dt;                    // δv += -R * b_a * dt
    Phi.block<3, 3>(6, 12) = -R * dt;                   // δθ += -R * b_g * dt
    
    // Second-order terms ((F_x * Δt)² / 2) - most significant
    double dt2_half = 0.5 * dt * dt;
    Phi.block<3, 3>(0, 6) = -R * accel_skew * dt2_half; // δp += -R*[a]× * δθ * dt²/2
    Phi.block<3, 3>(0, 9) = -R * dt2_half;              // δp += -R * b_a * dt²/2
    
    return Phi;
}

/**
 * @brief Compute Process Noise Covariance (Q_k)
 * 
 * Continuous-time noise model:
 *   w = [n_a, n_g, n_ba, n_bg]^T (12 dimensions)
 *   
 * Where:
 *   n_a:  Accelerometer white noise
 *   n_g:  Gyroscope white noise
 *   n_ba: Accelerometer bias random walk
 *   n_bg: Gyroscope bias random walk
 * 
 * Continuous-time noise covariance:
 *   Q_c = diag(σ_a², σ_g², σ_ba², σ_bg²)
 * 
 * Discrete-time process noise:
 *   Q_k = ∫[0,Δt] Φ(τ) * G * Q_c * G^T * Φ(τ)^T dτ
 * 
 * For small Δt, first-order approximation:
 *   Q_k ≈ G * Q_c * G^T * Δt
 * 
 * Where G is the noise input matrix:
 *   G = [ 0   0   0   0  ]  (position - no direct noise)
 *       [ R   0   0   0  ]  (velocity - accel noise)
 *       [ 0   R   0   0  ]  (orientation - gyro noise)
 *       [ 0   0   I   0  ]  (accel bias - random walk)
 *       [ 0   0   0   I  ]  (gyro bias - random walk)
 */
inline Matrix15d computeProcessNoiseCovariance(
    const Quaterniond& orientation,
    const IMUNoiseParams& noise_params,
    double dt = DT) {
    
    Matrix15d Q = Matrix15d::Zero();
    Matrix3d R = quaternionToRotationMatrix(orientation);
    
    // Accelerometer noise contribution to velocity error
    double accel_var = noise_params.accel_noise_density * noise_params.accel_noise_density;
    Q.block<3, 3>(3, 3) = R * Matrix3d::Identity() * R.transpose() * accel_var * dt;
    
    // Gyroscope noise contribution to orientation error
    double gyro_var = noise_params.gyro_noise_density * noise_params.gyro_noise_density;
    Q.block<3, 3>(6, 6) = R * Matrix3d::Identity() * R.transpose() * gyro_var * dt;
    
    // Accelerometer bias random walk
    double accel_rw_var = noise_params.accel_random_walk * noise_params.accel_random_walk;
    Q.block<3, 3>(9, 9) = Matrix3d::Identity() * accel_rw_var * dt;
    
    // Gyroscope bias random walk
    double gyro_rw_var = noise_params.gyro_random_walk * noise_params.gyro_random_walk;
    Q.block<3, 3>(12, 12) = Matrix3d::Identity() * gyro_rw_var * dt;
    
    return Q;
}

/**
 * @brief Propagate nominal state using IMU measurements
 * 
 * Nominal state kinematics (continuous-time):
 *   ṗ = v
 *   v̇ = R * (a - b_a) + g
 *   q̇ = 0.5 * q ⊗ [0, ω - b_g]^T
 *   ḃ_a = 0
 *   ḃ_g = 0
 * 
 * Discretization using RK4 (4th-order Runge-Kutta) for accuracy.
 */
inline void propagateNominalState(
    ESEKFState& state,
    const IMUMeasurement& imu,
    double dt = DT) {
    
    // Bias-corrected measurements
    Vector3d accel_corrected = imu.accel - state.accel_bias;
    Vector3d gyro_corrected = imu.gyro - state.gyro_bias;
    
    // Gravity vector in ENU frame
    Vector3d gravity(0, 0, -GRAVITY);
    
    // Rotation matrix
    Matrix3d R = quaternionToRotationMatrix(state.orientation);
    
    // Position update (using current velocity)
    state.position += state.velocity * dt + 0.5 * (R * accel_corrected + gravity) * dt * dt;
    
    // Velocity update
    state.velocity += (R * accel_corrected + gravity) * dt;
    
    // Orientation update (quaternion integration)
    Vector3d delta_angle = gyro_corrected * dt;
    Quaterniond delta_q = rotationVectorToQuaternion(delta_angle);
    state.orientation = state.orientation * delta_q;
    state.orientation.normalize();
    
    // Biases remain constant (updated during measurement correction)
    
    // Update timestamp
    state.timestamp = imu.timestamp;
}

/**
 * @brief Propagate error state covariance
 * 
 * Covariance propagation:
 *   P_k = Φ_k * P_{k-1} * Φ_k^T + Q_k
 */
inline void propagateErrorCovariance(
    ESEKFState& state,
    const Vector3d& accel_measurement,
    const IMUNoiseParams& noise_params,
    double dt = DT) {
    
    Matrix15d Phi = computeStateTransitionMatrix(state.orientation, accel_measurement, dt);
    Matrix15d Q = computeProcessNoiseCovariance(state.orientation, noise_params, dt);
    
    state.covariance = Phi * state.covariance * Phi.transpose() + Q;
    
    // Ensure symmetry (numerical stability)
    state.covariance = 0.5 * (state.covariance + state.covariance.transpose());
}

/**
 * @brief Inject error state into nominal state and reset
 * 
 * After measurement update, the error state is injected back into the nominal state:
 *   p ← p + δp
 *   v ← v + δv
 *   q ← q ⊗ [1, δθ/2]^T
 *   b_a ← b_a + δb_a
 *   b_g ← b_g + δb_g
 * 
 * Then reset error state to zero:
 *   δx ← 0
 */
inline void injectErrorState(ESEKFState& state) {
    // Extract error state components
    Vector3d delta_p = state.error_state.segment<3>(0);
    Vector3d delta_v = state.error_state.segment<3>(3);
    Vector3d delta_theta = state.error_state.segment<3>(6);
    Vector3d delta_ba = state.error_state.segment<3>(9);
    Vector3d delta_bg = state.error_state.segment<3>(12);
    
    // Inject into nominal state
    state.position += delta_p;
    state.velocity += delta_v;
    
    // Orientation injection (quaternion multiplication)
    Quaterniond delta_q = rotationVectorToQuaternion(delta_theta);
    state.orientation = state.orientation * delta_q;
    state.orientation.normalize();
    
    state.accel_bias += delta_ba;
    state.gyro_bias += delta_bg;
    
    // Reset error state
    state.error_state.setZero();
}

} // namespace indra_eye

#endif // INDRA_EYE_CORE_EKF_MATH_HPP
