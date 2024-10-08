# AR4 Hand Eye Calibration

Performs hand-eye calibration between a camera and the Annin Robotics AR4 robotic arm,
and validates calibration results. An Intel RealSense camera is used as an example,
but any camera can be substituted. Tested with ROS 2 Iron on Ubuntu 22.04.

[![Hand-Eye Calibration Demo](http://img.youtube.com/vi/w3tWKYnLL98/0.jpg)](https://youtu.be/w3tWKYnLL98)

The core calibration procedure uses [easy_handeye2](https://github.com/marcoesposito1988/easy_handeye2).

## Preparation

Print an Aruco marker and attach it to the end of J6. Aruco marker can be printed using
[ros2_aruco](https://github.com/JMU-ROBOTICS-VIVA/ros2_aruco?tab=readme-ov-file#generating-marker-images).

Verify that the Aruco marker parameters in `config/aruco_parameters.yaml` is correct for
your marker.

Note: You may want to 3D print an extra J6 gripper mount for this purpose.

## Installation

Clone this repo and [ar4_ros_driver](https://github.com/ycheng517/ar4_ros_driver) in the same ROS workspace.
i.e.

```bash
mkdir -p ~/ar4_ws/src
cd ~/ar4_ws/src
git clone https://github.com/ycheng517/ar4_ros_driver
git clone https://github.com/ycheng517/ar4_hand_eye_calibration
```

Import required repos with:

```bash
vcs import . --input ar4_hand_eye_calibration/hand_eye_calibration.repos
```

Install the required drivers and ROS 2 nodes for your camera. For example for Intel RealSense:

```bash
sudo apt install ros-iron-librealsense2* ros-iron-realsense2-*
```

Install dependencies of imported repos:

```bash
sudo apt update && rosdep install --from-paths . --ignore-src -y
```

## Calibrate

In one terminal, launch the hardware interface without including the gripper:

```bash
ros2 launch ar_hardware_interface ar_hardware.launch.py calibrate:=True include_gripper:=False
```

In another terminal, launch programs needed for calibration:

```bash
ros2 launch ar4_hand_eye_calibration calibrate.launch.py
```

Using RViz, move the robot end effector such that the Aruco marker is in view of the camera. Then, a
calibration GUI should appear on the screen. Use it to take a sample. Then move the end effector
to a few different orientations, take a sample at each orientation. When you have 5-6 samples, you
can save and exit all programs.

## Validate

In one terminal, launch the hardware interface without including the gripper:

```bash
ros2 launch ar_hardware_interface ar_hardware.launch.py calibrate:=True include_gripper:=False
```

In another terminal, launch programs needed for validation:

```bash
ros2 launch ar4_hand_eye_calibration validate.launch.py
```

Move an Aruco marker around the camera'a field of view. The robot arm should follow and hover above
the Aruco marker.
