# PlantHealthStatus.msg
# =====================================================================
# Custom ROS 2 message for V2 (The Doctor) thermal anomaly reports.
#
# Kid Translation: "This is the doctor's prescription. It says WHICH
# plant is sick, WHERE it is in the field (X, Y, Z coordinates), and
# HOW sick it is (confidence score). The Sprayer (V3) reads this note
# and goes to exactly the right spot."
# =====================================================================

# -- HEADER --
# Standard ROS 2 timestamp + frame_id (frame: "map" or "local_NED")
std_msgs/Header header

# -- ANOMALY IDENTITY --
# Unique sequential ID for this detection event
uint32 plant_id

# -- WORLD COORDINATES (NED frame, metres from home) --
# X = North, Y = East, Z = Down (negative = altitude above home)
float64 world_x
float64 world_y
float64 world_z

# -- IMAGE COORDINATES (pixel centroid in thermal frame) --
uint32 image_pixel_x
uint32 image_pixel_y

# -- CONFIDENCE & SEVERITY --
# confidence: 0.0 – 1.0 (fraction of hotspot area vs healthy)
float32 confidence

# severity: 0=WATCH, 1=MODERATE, 2=CRITICAL
uint8 severity
uint8 SEVERITY_WATCH    = 0
uint8 SEVERITY_MODERATE = 1
uint8 SEVERITY_CRITICAL = 2

# -- THERMAL METRICS --
# Raw pixel intensity of the detected hotspot centroid
uint8  hotspot_intensity
# Number of pixels in the detected cluster
uint32 cluster_size_px

# -- STATUS STRING (human-readable summary log) --
string description
