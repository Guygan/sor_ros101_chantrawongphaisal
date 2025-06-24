import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class CylinderInputNode(Node):
    def __init__(self):
        super().__init__('cylinder_input')
        self.publisher_ = self.create_publisher(Float64MultiArray, 'cylinder_properties', 10)
        timer_period = 2.0  # publish ทุก 2 วินาที
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        radius = float(input("Enter radius: "))
        height = float(input("Enter height: "))
        density = float(input("Enter density: "))
        msg = Float64MultiArray()
        msg.data = [radius, height, density]
        self.publisher_.publish(msg)
        self.get_logger().info(f'Published: radius={radius}, height={height}, density={density}')

def main(args=None):
    rclpy.init(args=args)
    node = CylinderInputNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
