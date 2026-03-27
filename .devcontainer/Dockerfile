FROM osrf/ros:humble-desktop

# Add ubuntu user with same UID and GID as your host system, if it doesn't already exist
# Since Ubuntu 24.04, a non-root user is created by default with the name vscode and UID=1000
ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN if ! id -u $USER_UID >/dev/null 2>&1; then \
    groupadd --gid $USER_GID $USERNAME && \
    useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi
# Add sudo support for the non-root user
RUN apt-get update && \
    apt-get install -y sudo && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Switch from root to user
USER $USERNAME

# Add user to video group to allow access to webcam
RUN sudo usermod --append --groups video $USERNAME

# Update all packages
RUN sudo apt update && sudo apt upgrade -y

# Install Git
RUN sudo apt install -y git

# Rosdep update
RUN rosdep update

# Source the ROS setup file
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc


################################
## ADD ANY CUSTOM SETUP BELOW ##
################################

# --- Установка текстового редактора
RUN sudo apt install gedit -y
# RUN sudo apt install nano -y

RUN sudo apt install tree -y

# --- Установка python3
RUN sudo apt install python3-pip -y

RUN pip install ultralytics

# --- Install Gazebo (https://gazebosim.org/docs/fortress/install_ubuntu/) or (https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#pc-setup)
RUN sudo apt-get install ros-${ROS_DISTRO}-ros-gz -y
RUN sudo apt install ros-${ROS_DISTRO}-gazebo-* -y
RUN sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
RUN sudo apt-get update -y
# RUN sudo apt install ros-humble-gazebo-ros-pkgs -y
RUN sudo apt-get install ignition-fortress -y

# --- Install Moveit
RUN sudo apt install ros-humble-moveit -y

# --- Install Cartographer
RUN sudo apt install ros-humble-cartographer -y
RUN sudo apt install ros-humble-cartographer-ros -y

# --- Install Navigation2
RUN sudo apt install ros-humble-navigation2 -y
RUN sudo apt install ros-humble-nav2-bringup -y

RUN echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
RUN bash -c 'source ~/.bashrc'