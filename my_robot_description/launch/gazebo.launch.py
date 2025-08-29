import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share_dir = get_package_share_directory('my_robot_description')
    urdf_path = os.path.join(pkg_share_dir, 'urdf', 'my_robot.urdf.xacro')

    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description_content}]
    )

    robot_name = 'my_robot'
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        # แก้ไข 'robot_ฟหกฟdescription' เป็น 'robot_description'
        arguments=['-topic', 'robot_description', '-name', robot_name],
        output='screen'
    )

    # สร้าง Bridge โดยใช้ Absolute Path เพื่อหลีกเลี่ยงปัญหา Environment
    # *** แก้ไขส่วนนี้ ***
    bridge_config_path = '/home/guygan/ros2_ws/src/my_robot_description/config/gz_bridge.yaml'


    gz_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # 'scan' ถูกจัดการในไฟล์ config แล้ว
            'odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            'tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            'joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            'cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        parameters=[{
            'config_file': bridge_config_path,
            'use_sim_time': True
        }],
        output='screen'
    )

    keyboard_teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_keyboard',
        output='screen',
        prefix='xterm -e'
    )

    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_robot,
        gz_ros_bridge,
        keyboard_teleop_node
    ])
