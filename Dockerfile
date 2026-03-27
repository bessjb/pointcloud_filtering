FROM ros:humble

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble
ENV WS_DIR=/ros2_ws

# Basic tooling and ROS build dependencies
RUN apt-get update && apt-get install -y \
    ros-humble-rviz2 \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-dev \
    build-essential \
    git \
    wget \
    curl \
    nano \
    vim \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Open3D
RUN pip3 install --no-cache-dir open3d

# Initialize rosdep if needed
RUN rosdep init 2>/dev/null || true && rosdep update


ENV DEBIAN_FRONTEND=noninteractive
ENV LIBGL_ALWAYS_INDIRECT=1

# Add user
RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

# Create workspace
RUN mkdir -p ${WS_DIR}/src
RUN chown -R qtuser:qtuser ${WS_DIR}

USER qtuser

# Install ROS package dependencies
RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    apt-get update && \
    rosdep install --from-paths src --ignore-src -r -y || true

WORKDIR ${WS_DIR}

# Copy workspace source if you want it baked into image
# If you prefer bind-mounting your local src folder at runtime, you can remove this
COPY ./src ${WS_DIR}/src

# Build workspace
RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink || true

# Automatically source ROS + workspace overlay in shell
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/qtuser/.bashrc && \
    echo "if [ -f ${WS_DIR}/install/setup.bash ]; then source ${WS_DIR}/install/setup.bash; fi" >> /home/qtuser/.bashrc

CMD ["/bin/bash"]
