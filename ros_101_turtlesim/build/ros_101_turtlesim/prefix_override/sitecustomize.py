import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/guygan/ros2_ws/src/sor_ros101_chantrawongphaisal/ros_101_turtlesim/install/ros_101_turtlesim'
