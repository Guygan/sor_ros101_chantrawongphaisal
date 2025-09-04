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
    pkg_share_dir = get_package_share_directory('my_robot_description')
    urdf_path = os.path.join(pkg_share_dir, 'urdf', 'my_robot.urdf.xacro')
    slam_params_path = os.path.join(pkg_share_dir, 'config', 'my_slam_params.yaml')
    rviz_config_path = os.path.join(pkg_share_dir, 'rviz', 'slam_view.rviz') # เราจะสร้างไฟล์นี้ใหม่

    robot_description_content = ParameterValue(Command(['xacro ', urdf_path]), value_type=str)

    # --- ส่วนที่ 1: เปิด Gazebo และ Node พื้นฐาน ---
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description_content}]
    )
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot'],
        output='screen'
    )
    # ✅ Bridge ยังคงต้องใช้ แต่ไม่ต้องสนใจเรื่อง frame_id_mappings อีกต่อไป
    parameter_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='parameter_bridge',
        parameters=[{'config_file': os.path.join(pkg_share_dir, 'config', 'gz_bridge.yaml')}],
        output='screen'
    )
    # ✅ เปิด Node ใหม่ที่เราสร้างขึ้นมา
    frame_fixer_node = Node(
        package='my_robot_description',
        executable='frame_fixer',
        name='scan_frame_fixer'
    )
    teleop_twist_keyboard_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e'
    )

    # --- ส่วนที่ 2: เตรียม SLAM และ RViz ---
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params_path, {'use_sim_time': True}]
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
            target_action=spawn_robot,
            on_exit=[slam_toolbox_node, rviz_node]
        )
    )

    # --- ส่วนสุดท้าย: รวมทุกอย่าง ---
    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_robot,
        parameter_bridge,
        frame_fixer_node, # <-- เพิ่ม Node ใหม่ที่นี่
        teleop_twist_keyboard_node,
        delayed_nodes_handler
    ])