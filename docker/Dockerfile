# ============================================================================
# 🚁 PHD RESEARCH LAB - GOLDEN MASTER (FIXED)
# Version: 3.1
# Base: Official PX4 Image (Ubuntu 22.04 + ROS2 Humble)
# Fixes: Corrected Base Image Name + Matplotlib Patch
# ============================================================================

# ✅ FIX: Added the '2' in ros2-humble
FROM px4io/px4-dev-simulation-jammy

# --- 🛠️ 1. GLOBAL ENVIRONMENT SETUP ---
ENV DEBIAN_FRONTEND=noninteractive
ENV WORKSPACE_DIR=/root/hexacopter_phd
ENV TERM=xterm-256color
ENV ROS_DISTRO=humble
# Force PX4 to use the modern Gazebo (Garden/Harmonic)
ENV PX4_GZ_STANDALONE=1

# Initialize the Build Progress Log
RUN touch /root/build_progress.log

# --- 🔵 PHASE 1: SYSTEM FOUNDATION ---
RUN echo "🚀 PHASE 1: Installing System Tools..." \
    && apt-get update && apt-get install -y \
        locales tzdata git wget curl vim nano build-essential cmake \
        python3-pip python3-dev lsb-release gnupg2 sudo iputils-ping \
        software-properties-common \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 \
    && echo "✅ PHASE 1 COMPLETE" >> /root/build_progress.log

# --- 🔵 PHASE 2: COMMUNICATION BRIDGE (Micro XRCE-DDS) ---
WORKDIR /root
RUN echo "🚀 PHASE 2: Installing XRCE-DDS Bridge..." \
    && git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git \
    && cd Micro-XRCE-DDS-Agent && mkdir build && cd build \
    && cmake .. && make && make install && ldconfig /usr/local/lib/ \
    && echo "✅ PHASE 2 COMPLETE" >> /root/build_progress.log

# --- 🔵 PHASE 3: FLIGHT CONTROL STACK ---
WORKDIR /root
RUN echo "🚀 PHASE 3: Installing PX4 Autopilot..." \
    && git clone -b v1.14.0 https://github.com/PX4/PX4-Autopilot.git --recursive \
    && cd PX4-Autopilot \
    # ⚠️ CRITICAL FIX: Patch broken python requirements
    && sed -i 's/matplotlib>=3.0.*/matplotlib>=3.0/g' Tools/setup/requirements.txt \
    # Run setup script
    && bash ./Tools/setup/ubuntu.sh --no-nuttx \
    && echo "✅ PHASE 3 COMPLETE" >> /root/build_progress.log

# --- 🔵 PHASE 4: COMPILING SIMULATION ---
WORKDIR /root/PX4-Autopilot
RUN echo "🚀 PHASE 4: Compiling Simulation Binary..." \
    # ⚠️ CRITICAL FIX: Use 'gz_x500' target
    && DONT_RUN=1 make px4_sitl gz_x500 \
    && echo "✅ PHASE 4 COMPLETE" >> /root/build_progress.log

# --- 🔵 PHASE 5: AI & VISION TOOLS ---
RUN echo "🚀 PHASE 5: Installing AI Engines..." \
    && pip3 install --upgrade pip \
    && pip3 install \
        tensorflow==2.13.0 \
        opencv-python-headless \
        numpy \
        matplotlib \
        scipy \
        pandas \
    && echo "✅ PHASE 5 COMPLETE" >> /root/build_progress.log

# --- 🔵 PHASE 6: ROS2 WORKSPACE ---
WORKDIR $WORKSPACE_DIR/src
RUN echo "🚀 PHASE 6: Building ROS2 Workspace..." \
    && git clone -b release/1.14 https://github.com/PX4/px4_msgs.git \
    && cd .. \
    && /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build" \
    && echo "✅ PHASE 6 COMPLETE" >> /root/build_progress.log

# --- 🔵 PHASE 7: FINAL SETUP ---
WORKDIR $WORKSPACE_DIR
RUN echo '#!/bin/bash' > /root/startup.sh \
    && echo 'echo "🚁 PHD LAB READY. LOGS:"' >> /root/startup.sh \
    && echo 'cat /root/build_progress.log' >> /root/startup.sh \
    && echo 'source /opt/ros/humble/setup.bash' >> /root/startup.sh \
    && echo 'source /root/hexacopter_phd/install/setup.bash' >> /root/startup.sh \
    && echo 'export UXRCE_DDS_PT=8888' >> /root/startup.sh \
    && echo 'alias sim_start="cd /root/PX4-Autopilot && make px4_sitl gz_x500"' >> /root/startup.sh \
    && echo 'alias bridge_start="MicroXRCEAgent udp4 -p 8888"' >> /root/startup.sh \
    && echo 'exec "$@"' >> /root/startup.sh \
    && chmod +x /root/startup.sh

RUN echo "source /root/startup.sh" >> /root/.bashrc

ENTRYPOINT ["/root/startup.sh"]
CMD ["bash"]
