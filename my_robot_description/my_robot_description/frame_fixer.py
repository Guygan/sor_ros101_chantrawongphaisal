import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

class FrameFixer(Node):
    def __init__(self):
        super().__init__('scan_frame_fixer')
        self.publisher_ = self.create_publisher(LaserScan, '/scan_corrected', 10)
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.listener_callback,
            10)
        self.get_logger().info('Scan Frame Fixer node has started.')

    def listener_callback(self, msg):
        msg.header.frame_id = 'lidar_link'
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FrameFixer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()