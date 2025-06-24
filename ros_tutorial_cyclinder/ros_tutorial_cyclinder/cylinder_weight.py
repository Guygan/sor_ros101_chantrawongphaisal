#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Float64MultiArray
import math

class CylinderWeightNode(Node):
    def __init__(self):
        super().__init__('cylinder_weight')

        self.weight_pub = self.create_publisher(Float64, '/cylinder_weight', 10)

        self.subscription = self.create_subscription(
            Float64MultiArray,
            'cylinder_properties',
            self.callback,
            10)

    def callback(self, msg):
        if len(msg.data) != 3:
            self.get_logger().warn('Expected 3 elements: radius, height, density')
            return

        radius, height, density = msg.data
        volume = math.pi * radius ** 2 * height
        weight = volume * density

        self.get_logger().info(f'Weight = {weight:.2f}')
        self.weight_pub.publish(Float64(data=weight))

def main(args=None):
    rclpy.init(args=args)
    node = CylinderWeightNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
