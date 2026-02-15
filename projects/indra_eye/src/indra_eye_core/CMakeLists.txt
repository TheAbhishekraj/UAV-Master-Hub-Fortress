cmake_minimum_required(VERSION 3.8)
project(indra_eye_core)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(diagnostic_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

# Include directories
include_directories(
  include
  ${EIGEN3_INCLUDE_DIR}
)

# ES-EKF Node executable
add_executable(es_ekf_node src/es_ekf_node.cpp)
ament_target_dependencies(es_ekf_node
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  diagnostic_msgs
  std_msgs
)

# MAVROS Bridge Node executable
add_executable(mavros_bridge_node src/mavros_bridge_node.cpp)
ament_target_dependencies(mavros_bridge_node
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  std_msgs
)

# Path Aggregator Node executable
add_executable(path_aggregator_node src/path_aggregator_node.cpp)
ament_target_dependencies(path_aggregator_node
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
)

# Install targets
install(TARGETS
  es_ekf_node
  mavros_bridge_node
  path_aggregator_node
  DESTINATION lib/${PROJECT_NAME}
)

# Install header files
install(DIRECTORY include/
  DESTINATION include/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
