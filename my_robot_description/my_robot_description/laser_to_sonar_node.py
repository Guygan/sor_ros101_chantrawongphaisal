import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Range
import math

class LaserToSonarNode(Node):
    def __init__(self):
        # เรียกใช้ constructor ของคลาสแม่ (Node) พร้อมตั้งชื่อ Node
        super().__init__('laser_to_sonar_node') 

        # กำหนดพารามิเตอร์สำหรับชื่อ topic ที่จะ publish และ subscribe
        self.declare_parameter('pub_topic', '/range') 
        self.declare_parameter('sub_topic', '/scan') 

        # ดึงค่าพารามิเตอร์ที่ประกาศไว้
        self.pub_topic = self.get_parameter('pub_topic').get_parameter_value().string_value
        self.sub_topic = self.get_parameter('sub_topic').get_parameter_value().string_value

        # สร้าง Publisher สำหรับ Range message
        self.publisher_ = self.create_publisher(Range, self.pub_topic, 10)
        self.get_logger().info(f"กำลังเผยแพร่ไปยัง topic: {self.pub_topic}")

        # สร้าง Subscriber สำหรับ LaserScan message
        self.subscription = self.create_subscription(
            LaserScan,
            self.sub_topic,
            self.laser_scan_callback, # กำหนดฟังก์ชัน callback เมื่อได้รับข้อความ
            10
        )
        self.get_logger().info(f"กำลังสมัครรับข้อมูลจาก topic: {self.sub_topic}")
        self.subscription  # ป้องกัน warning เรื่องตัวแปรไม่ได้ถูกใช้

    def laser_scan_callback(self, data: LaserScan):
        # Log ค่าระยะแรก (คล้ายกับ rospy.loginfo ใน ROS 1)
        # ตรวจสอบว่า data.ranges ไม่ว่างเปล่า เพื่อป้องกัน error
        if data.ranges:
            self.get_logger().debug(self.get_name() + f" ได้รับข้อมูล: {data.ranges[0]}")
        else:
            self.get_logger().warn(self.get_name() + " ได้รับข้อมูล LaserScan ranges ว่างเปล่า")
            return # ออกจากฟังก์ชันถ้าไม่มีข้อมูลระยะ

        range_msg = Range()
        
        # ใส่ข้อมูล Header
        range_msg.header.stamp = self.get_clock().now().to_msg() # ดึงเวลาปัจจุบันสำหรับ ROS 2
        range_msg.header.frame_id = data.header.frame_id # ใช้ frame_id จาก LaserScan

        # กำหนดคุณสมบัติคงที่สำหรับ Range message
        range_msg.radiation_type = Range.ULTRASOUND # ประเภทการแผ่รังสี
        range_msg.field_of_view = 0.0698132 # มุมมอง (เป็นเรเดียน)
        range_msg.min_range = 0.1 # ระยะทางต่ำสุดที่เซ็นเซอร์ตรวจจับได้
        range_msg.max_range = 30.0 # ระยะทางสูงสุดที่เซ็นเซอร์ตรวจจับได้

        # ค้นหาระยะทางที่ใกล้ที่สุดจากข้อมูล LaserScan
        # กรองค่า 'inf' (infinity) ซึ่งหมายถึงไม่พบสิ่งกีดขวาง
        valid_ranges = [r for r in data.ranges if not math.isinf(r)]
        if valid_ranges:
            range_msg.range = min(valid_ranges) # ใช้ค่าน้อยที่สุด
        else:
            # ถ้าไม่พบค่าระยะที่ถูกต้อง ให้ตั้งค่าเป็น max_range หรือค่าอื่นที่ระบุว่าไม่มีสิ่งกีดขวาง
            range_msg.range = range_msg.max_range 
            self.get_logger().warn(self.get_name() + " ไม่พบค่าระยะที่ถูกต้อง, กำหนดระยะเป็นค่าสูงสุด.")

        # เผยแพร่ Range message
        self.publisher_.publish(range_msg)


def main(args=None):
    rclpy.init(args=args) # เริ่มต้น rclpy

    node = LaserToSonarNode() # สร้าง Node

    try:
        rclpy.spin(node) # ทำให้ Node ทำงานต่อไปจนกว่าจะถูกขัดจังหวะ
    except KeyboardInterrupt:
        node.get_logger().info('Node ถูกหยุดอย่างเรียบร้อย')
    finally:
        node.destroy_node() # ทำลาย Node เมื่อไม่ใช้งาน
        rclpy.shutdown() # ปิด rclpy


if __name__ == '__main__':
    main()
