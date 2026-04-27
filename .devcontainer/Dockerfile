FROM osrf/ros:humble-desktop

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_NO_CACHE_DIR=1

ARG INSTALL_VISION_DEPS=false
ENV INSTALL_VISION_DEPS=${INSTALL_VISION_DEPS}

# Add ubuntu user with same UID and GID as your host system, if it doesn't already exist
# Since Ubuntu 24.04, a non-root user is created by default with the name vscode and UID=1000
ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    clang-format \
    gdb \
    gedit \
    gazebo \
    ros-${ROS_DISTRO}-gazebo-ros-pkgs \
    ros-${ROS_DISTRO}-turtlesim \
    sudo \
    git \
    pkg-config \
    usbutils \
    udev \
    python3-pip \
    python3-serial \
    python3-venv \
    python3-opencv \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-setuptools \
    python3-wheel \
    tree \
    curl \
    ca-certificates \
    lsb-release \
    gnupg \
    stockfish \
    && rm -rf /var/lib/apt/lists/* && \
    if ! id -u $USER_UID >/dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME && \
        useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME && \
    usermod --append --groups video,dialout,plugdev $USERNAME

RUN python3 -m pip install --no-cache-dir \
    stockfish

# Switch from root to user
USER $USERNAME

# Source the ROS setup file
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc


################################
## ADD ANY CUSTOM SETUP BELOW ##
################################

# # --- Install Moveit
# RUN sudo apt install ros-humble-moveit -y

# # --- Install Cartographer
# RUN sudo apt install ros-humble-cartographer -y
# RUN sudo apt install ros-humble-cartographer-ros -y

# # --- Install Navigation2
# RUN sudo apt install ros-humble-navigation2 -y
# RUN sudo apt install ros-humble-nav2-bringup -y

RUN echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc