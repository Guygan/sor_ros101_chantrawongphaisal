#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Float64MultiArray  # <-- เพิ่ม Float64MultiArray

class CylinderSubscriberNode(Node):
    def __init__(self):
        super().__init__('cylinder_squared')

        self.area_pub = self.create_publisher(Float64, '/radius_squared', 10)

        self.radius_sub = self.create_subscription(
            Float64MultiArray,     # ต้องเป็นชนิดนี้ ถ้ารับจาก 'cylinder_properties'
            'cylinder_properties',
            self.radius_callback,
            10)

    def radius_callback(self, msg):
        radius = msg.data[0]
        area = radius * radius
        self.get_logger().info(f'Area = {area:.2f}')
        self.area_pub.publish(Float64(data=area))

def main(args=None):
    rclpy.init(args=args)
    node = CylinderSubscriberNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
