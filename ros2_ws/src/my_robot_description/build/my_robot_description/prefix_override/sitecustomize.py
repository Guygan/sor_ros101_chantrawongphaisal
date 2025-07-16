import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/guygan/ros2_ws/src/my_robot_description/install/my_robot_description'
