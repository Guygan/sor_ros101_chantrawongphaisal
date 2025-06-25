#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class TurtleGuide(Node):
    def __init__(self, target_x, target_y, threshold=0.1):
        super().__init__('turtle_guide_to_xy')

        self.target_x = target_x
        self.target_y = target_y
        self.threshold = threshold

        # Publisher and Subscriber
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscriber = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)

        self.get_logger().info(f'Moving to ({self.target_x:.2f}, {self.target_y:.2f})')

    def pose_callback(self, msg: Pose):
        # Log current pose (DEBUG)
        self.get_logger().debug(f'Current position: x={msg.x:.2f}, y={msg.y:.2f}, theta={msg.theta:.2f}')

        dx = self.target_x - msg.x
        dy = self.target_y - msg.y
        distance = math.hypot(dx, dy)

        if distance < self.threshold:
            self.get_logger().info('Target Reached')
            self.publisher.publish(Twist())  # Stop
            return

        # Calculate angle to goal
        angle_to_goal = math.atan2(dy, dx)
        angle_diff = angle_to_goal - msg.theta
        angle_diff = math.atan2(math.sin(angle_diff), math.cos(angle_diff))  # Normalize to [-π, π]

        cmd = Twist()
        cmd.linear.x = min(1.5 * distance, 2.0)
        cmd.angular.z = 4.0 * angle_diff
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)

    try:
        target_x = float(input("Enter target X: "))
        target_y = float(input("Enter target Y: "))
        threshold = float(input("Enter threshold radius (default=0.1): ") or 0.1)
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return

    node = TurtleGuide(target_x, target_y, threshold)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
