# SprayCommand.msg
# =====================================================================
# Custom ROS 2 message for V3 (The Helper) spray activation commands.
#
# Kid Translation: "This is the medicine label. It tells the sprayer
# drone: go to X, Y, Z in the field and spray exactly 5ml of medicine
# on Plant #7."
# =====================================================================

# -- HEADER --
std_msgs/Header header

# -- TARGET IDENTITY --
# Links back to the PlantHealthStatus.plant_id that triggered this spray
uint32 plant_id

# -- WORLD TARGET COORDINATES (NED, metres from home) --
float64 target_x
float64 target_y
float64 target_z

# -- SPRAY PARAMETERS --
# Requested dose in millilitres (simulated in Gazebo)
float32 dose_ml

# Duration to hold sprayer valve open (seconds)
float32 spray_duration_sec

# -- COMMAND STATUS --
# 0=PENDING, 1=NAVIGATING, 2=SPRAYING, 3=COMPLETE, 4=ABORT
uint8 status
uint8 STATUS_PENDING    = 0
uint8 STATUS_NAVIGATING = 1
uint8 STATUS_SPRAYING   = 2
uint8 STATUS_COMPLETE   = 3
uint8 STATUS_ABORT      = 4
