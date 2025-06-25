#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import math

class SquareTurtleNode(Node):
    def __init__(self):
        super().__init__('square_turtle')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.move_square()

    def move_square(self):
        msg = Twist()
        for _ in range(4):
            # Move forward
            start_time = time.time()
            while (time.time() - start_time) < 1.0:
                msg.linear.x = 0.2
                msg.angular.z = 0.0
                self.publisher_.publish(msg)
                time.sleep(0.1)
            msg.linear.x = 0.0
            self.publisher_.publish(msg)
            time.sleep(0.5)

            # Turn right
            start_time = time.time()
            while (time.time() - start_time) < 1.0:
                msg.linear.x = 0.0
                msg.angular.z = math.pi / 2.0
                self.publisher_.publish(msg)
                time.sleep(0.1)
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            time.sleep(0.5)

def main(args=None):
    rclpy.init(args=args)
    node = SquareTurtleNode()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
