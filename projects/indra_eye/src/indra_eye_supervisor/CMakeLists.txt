cmake_minimum_required(VERSION 3.8)
project(indra_eye_supervisor)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

# Include directories
include_directories(
  ${EIGEN3_INCLUDE_DIR}
)

# Supervisor Node executable
add_executable(supervisor_node src/supervisor_node.cpp)
ament_target_dependencies(supervisor_node
  rclcpp
  sensor_msgs
  nav_msgs
  std_msgs
)

# Install targets
install(TARGETS
  supervisor_node
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
