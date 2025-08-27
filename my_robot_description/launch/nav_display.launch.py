import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # --- Paths ---
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    nav2_bringup_pkg_dir = get_package_share_directory('nav2_bringup')
    
    # --- Configurations ---
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    #  vvv  แก้ไขบรรทัดนี้เท่านั้น vvv
    nav2_params_file = os.path.join(my_robot_pkg_dir, 'config', 'nav2_params.yaml')
    #  ^^^  แก้ไขบรรทัดนี้เท่านั้น ^^^
    map_file = os.path.join(my_robot_pkg_dir, 'maps', 'my_map.yaml')

    # --- Include Gazebo simulation launch file ---
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(my_robot_pkg_dir, 'launch', 'gazebo.launch.py')
        )
    )

    # --- Include Nav2 bringup launch file ---
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': nav2_params_file,
            'map': map_file,
        }.items()
    )

    # --- RViz2 Node ---
    rviz_config_file = os.path.join(nav2_bringup_pkg_dir, 'rviz', 'nav2_default_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        gazebo_launch,
        nav2_bringup_launch,
        rviz_node
    ])