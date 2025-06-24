#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Float64MultiArray
import math

class CylinderVolumeNode(Node):
    def __init__(self):
        super().__init__('cylinder_volume')

        # subscribe ค่า height จาก cylinder_properties
        self.height = None

        self.volume_pub = self.create_publisher(Float64, '/cylinder_volume', 10)

        self.height_sub = self.create_subscription(
            Float64MultiArray,
            'cylinder_properties',
            self.height_callback,
            10)

        # subscribe ค่า area จาก /radius_squared
        self.area_sub = self.create_subscription(
            Float64,
            '/radius_squared',
            self.area_callback,
            10)

        self.area = None

    def height_callback(self, msg):
        if len(msg.data) < 2:
            self.get_logger().warn('Data must include at least [radius, height]')
            return
        self.height = msg.data[1]
        self.try_compute_volume()

    def area_callback(self, msg):
        self.area = msg.data
        self.try_compute_volume()

    def try_compute_volume(self):
        if self.area is not None and self.height is not None:
            volume = self.area * self.height
            self.get_logger().info(f'Cylinder Volume = {volume:.2f}')
            self.volume_pub.publish(Float64(data=volume))
        
            self.area = None
            self.height = None

def main(args=None):
    rclpy.init(args=args)
    node = CylinderVolumeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
