# my_robot_description/launch/nav2_slam.launch.py (ฉบับแก้ไข)

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    pkg_dir = get_package_share_directory('my_robot_description')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    world_path = os.path.join(pkg_dir, 'worlds', 'test_world.sdf')
    map_path = os.path.join(pkg_dir, 'maps', 'my_map.yaml')
    nav2_params_path = os.path.join(pkg_dir, 'config', 'nav2_params.yaml')
    rviz_config_path = os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')
    
    # --- FIX: เพิ่ม Path ไปยังไฟล์ EKF config ---
    ekf_config_path = os.path.join(pkg_dir, 'config', 'ekf.yaml')

    declare_world_arg = DeclareLaunchArgument('world', default_value=world_path)
    declare_map_arg = DeclareLaunchArgument('map', default_value=map_path)
    
    # --- ส่วนที่รัน Gazebo และส่วนประกอบพื้นฐานของหุ่นยนต์ ---
    # เราจะสมมติว่าคุณมี gazebo.launch.py ที่สมบูรณ์แล้ว
    start_gazebo_and_robot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    # --- FIX: สร้าง Node สำหรับ frame_fixer ---
    frame_fixer_node = Node(
        package='my_robot_description',
        executable='frame_fixer',
        name='scan_frame_fixer',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # --- ส่วนที่รันระบบนำทาง Nav2 ---
    start_nav2_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'use_sim_time': 'true',
            'params_file': nav2_params_path
        }.items()
    )

    # --- ส่วนที่รัน RViz ---
    start_rviz_cmd = Node(
        package='rviz2', executable='rviz2', name='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}], output='screen'
    )

    return LaunchDescription([
        declare_world_arg,
        declare_map_arg,
        start_gazebo_and_robot_cmd,
        
        # --- FIX: เพิ่ม frame_fixer_node เข้าไปใน list ที่จะรัน ---
        frame_fixer_node,
        
        start_nav2_cmd,
        start_rviz_cmd
    ])