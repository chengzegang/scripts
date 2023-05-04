FROM osrf/ros:humble-desktop
RUN apt-get update && apt-get install -y --no-install-recommends \
  ros-humble-gazebo-* \
  ros-humble-cartographer \
  ros-humble-cartographer-ros \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-dynamixel-sdk \
  ros-humble-turtlebot3-msgs \
  ros-humble-turtlebot3 \
COPY ./online.sh ~/online.sh
RUN chmod +x ~/online.sh
RUN echo "source ~/online.sh" >> ~/.bashrc
RUN source ~/.bashrc
CMD ["ros2", "launch", "turtlebot3_bringup", "robot.launch.py"]