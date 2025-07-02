#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo


class ArucoPoseEstimator(Node):
    """Node to estimate the pose of ArUco markers in the camera image.
    
    Run the following command to visualize the output:
    
    ros2 run image_view image_view image:=/aruco_image 
    """

    def __init__(self):
        super().__init__('aruco_pose_estimator')

        self.bridge = CvBridge()

        # Image subscriber
        self.image_subscription = self.create_subscription(
            Image,
            '/camera/color/image_raw',  # Correct topic
            self.image_callback,
            10)

        # CameraInfo subscriber for color camera
        self.camera_info_subscription = self.create_subscription(
            CameraInfo,
            '/camera/color/camera_info',  # Correct topic
            self.camera_info_callback,
            10)
        self.camera_info_received = False  # Flag to track if we have camera info

        # Initialize camera parameters (will be filled from CameraInfo)
        self.camera_matrix = None
        self.dist_coeffs = None

        # Aruco dictionary and parameters
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(
            cv2.aruco.DICT_5X5_250)
        self.aruco_params = cv2.aruco.DetectorParameters()

        # Image publisher
        self.image_publisher = self.create_publisher(Image, '/aruco_image', 10)

    def camera_info_callback(self, msg):
        # Extract camera matrix and distortion coefficients from CameraInfo message
        K = np.array(msg.k).reshape(3, 3)  # Intrinsic parameters
        D = np.array(msg.d)  # Distortion coefficients

        self.camera_matrix = K
        self.dist_coeffs = D

        self.camera_info_received = True  # Set the flag
        self.get_logger().info("Camera info received and parameters set.")

        # Unsubscribe after receiving the information (optional, but good practice)
        self.destroy_subscription(
            self.camera_info_subscription)  # No need to keep listening

    def image_callback(self, msg):
        if not self.camera_info_received:  # Don't process until we have camera info
            self.get_logger().warn("Waiting for camera info...")
            return

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return

        corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(
            cv_image, self.aruco_dict)

        if ids is not None:
            rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                corners, 0.07, self.camera_matrix,
                self.dist_coeffs)  # 0.1 is marker size

            for i in range(len(ids)):
                cv2.aruco.drawDetectedMarkers(cv_image, corners, ids)
                cv2.drawFrameAxes(cv_image, self.camera_matrix,
                                  self.dist_coeffs, rvecs[i], tvecs[i], 0.07)

        try:
            overlay_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
            self.image_publisher.publish(overlay_msg)
        except Exception as e:
            self.get_logger().error(f"Error publishing image: {e}")


def main(args=None):
    rclpy.init(args=args)
    aruco_pose_estimator = ArucoPoseEstimator()
    rclpy.spin(aruco_pose_estimator)
    aruco_pose_estimator.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
