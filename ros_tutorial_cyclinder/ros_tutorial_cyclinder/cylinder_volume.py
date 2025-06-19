#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray, Float64
import math

class CylinderVolumeNode(Node):
    def __init__(self):
        super().__init__('cylinder_volume')

        self.volume_pub = self.create_publisher(Float64, '/cylinder_volume', 10)

        self.subscription = self.create_subscription(
            Float64MultiArray,
            'cylinder_dimensions',
            self.dimensions_callback,
            10)

    def dimensions_callback(self, msg):
        if len(msg.data) != 2:
            self.get_logger().warn('Received data length is not 2')
            return
        radius, height = msg.data
        volume = math.pi * radius ** 2 * height
        self.get_logger().info(f'Cylinder Volume = {volume:.2f}')
        self.volume_pub.publish(Float64(data=volume))

def main(args=None):
    rclpy.init(args=args)
    node = CylinderVolumeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
