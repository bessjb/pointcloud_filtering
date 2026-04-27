FROM ros:humble

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive \
    ROS_DISTRO=humble \
    WS_DIR=/ros2_ws \
    LIBGL_ALWAYS_INDIRECT=1

RUN apt-get update && apt-get install -y \
    ros-humble-rviz2 \
    ros-humble-plotjuggler-ros \
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

RUN pip3 install --no-cache-dir open3d rosbags

RUN rosdep init 2>/dev/null || true && rosdep update

RUN adduser --quiet --disabled-password qtuser && usermod -a -G audio qtuser

WORKDIR ${WS_DIR}
RUN mkdir -p ${WS_DIR}/src

COPY ./src ${WS_DIR}/src

RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    apt-get update && \
    rosdep install --from-paths src --ignore-src -r -y || true

RUN chown -R qtuser:qtuser ${WS_DIR}

USER qtuser

RUN source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install

# Automatically source ROS + workspace overlay in shell
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/qtuser/.bashrc && \
    echo "if [ -f ${WS_DIR}/install/setup.bash ]; then source ${WS_DIR}/install/setup.bash; fi" >> /home/qtuser/.bashrc

CMD ["/bin/bash"]
