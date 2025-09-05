import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    urdf_path = os.path.join(my_robot_pkg_dir, 'urdf', 'my_robot.urdf.xacro')
    bridge_config_path = os.path.join(my_robot_pkg_dir, 'config', 'gz_bridge.yaml')
    rviz_config_path = os.path.join(my_robot_pkg_dir, 'rviz', 'slam_view.rviz')

    robot_description_content = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)

    # --- ส่วนที่ 1: เปิดโปรแกรมพื้นฐาน ---
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description_content}]
    )

    spawn_robot_action = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot'],
        output='screen'
    )

    gz_ros_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_ros_bridge',
        parameters=[{'config_file': bridge_config_path, 'use_sim_time': True}],
        output='screen'
    )

    frame_fixer_node = Node(
        package='my_robot_description',
        executable='frame_fixer',
        name='scan_frame_fixer',
        output='screen'
    )

    teleop_keyboard_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e'
    )

    # --- ส่วนที่ 2: เตรียม SLAM และ RViz (รอรันทีหลัง) ---
    
    # ✅✅✅ กำหนดค่า Parameter ของ SLAM โดยตรงที่นี่ ✅✅✅
    # เราจะไม่โหลดจากไฟล์ my_slam_params.yaml อีกต่อไป
    slam_params = {
        'use_sim_time': True,
        'odom_frame': 'odom',
        'map_frame': 'map',
        'base_frame': 'base_footprint',
        'scan_topic': '/scan_corrected', # <-- ใช้ Topic ที่ถูกต้อง
        'mode': 'mapping',
        # คุณสามารถเพิ่มพารามิเตอร์อื่นๆ จากไฟล์ .yaml เดิมของคุณที่นี่ได้
    }
    
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params] # <-- ใช้ Dictionary ที่เราสร้างขึ้นโดยตรง
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}]
    )

    # --- ส่วนที่ 3: ตัวจัดการลำดับ ---
    delayed_nodes_handler = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot_action,
            on_exit=[slam_toolbox_node, rviz_node]
        )
    )

    # --- ส่วนสุดท้าย: รวมทุกอย่าง ---
    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher_node,
        spawn_robot_action,
        gz_ros_bridge_node,
        frame_fixer_node,
        teleop_keyboard_node,
        delayed_nodes_handler
    ])