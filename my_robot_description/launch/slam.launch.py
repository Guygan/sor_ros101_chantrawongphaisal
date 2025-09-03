# /home/guygan/ros2_ws/src/my_robot_description/launch/slam.launch.py

import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # 1. เรียกใช้ Gazebo
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(my_robot_pkg_dir, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )
    
    # 2. สร้าง Bridge พร้อมโหลดไฟล์คอนฟิก
    gz_bridge_config = os.path.join(
        get_package_share_directory('my_robot_description'),
        'config',
        'gz_bridge.yaml'
    )
    parameter_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='parameter_bridge',
        parameters=[gz_bridge_config],
        output='screen'
    )
    
    # 3. เปิด Node 'slam_toolbox'
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            os.path.join(my_robot_pkg_dir, 'config', 'my_slam_params.yaml')
        ]
    )
    
    # 4. เปิดโปรแกรม RViz2
    rviz_config_file = os.path.join(my_robot_pkg_dir, 'rviz', 'urdf_config.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # --- ส่วนของการรวมทุกอย่างและส่งคืนผลลัพธ์ ---
    # ✅ เพิ่ม parameter_bridge เข้าไปในลิสต์นี้
    return LaunchDescription([
        use_sim_time_arg,
        gazebo_launch,
        parameter_bridge,  # <--- เพิ่มตรงนี้
        slam_toolbox_node,
        rviz_node
    ])