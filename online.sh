
HOSTNAME=$(whoami)


if [ -d "/usr/local/bin/husarnet-dds" ]; then
    RELEASE="v1.3.5"
    ARCH=$(uname -m)
    if [ $ARCH = "aarch64" ]; then
        export ARCH=arm64
    fi
    curl -s https://install.husarnet.com/install.sh | sudo bash
    sudo curl -L https://github.com/husarnet/husarnet-dds/releases/download/$RELEASE/husarnet-dds-linux-$ARCH -o /usr/local/bin/husarnet-dds
    sudo chmod +x /usr/local/bin/husarnet-dds
fi


ros2 daemon stop
source $HOME/.bashrc
export TB3_MODEL='burger'
export ROS_DOMAIN_ID=30
export ROS_TURTLEBOT3_MODEL=$TB3_MODEL
export HUSARNET_JOINCODE="fc94:b01d:1803:8dd8:b293:5c7d:7639:932a/aVWsS5bB6wf3fE9KviZK2C"
husarnet join $HUSARNET_JOINCODE $HOSTNAME

export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export FASTRTPS_DEFAULT_PROFILES_FILE=/var/tmp/husarnet-fastdds-simple.xml


source /opt/ros/humble/setup.bash
ros2 daemon start