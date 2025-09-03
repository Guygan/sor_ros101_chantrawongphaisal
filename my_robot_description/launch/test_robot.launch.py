# my_robot_description/launch/test_robot.launch.py
import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # รัน Gazebo เหมือนเดิม
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(my_robot_pkg_dir, 'launch', 'gazebo.launch.py')),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # รัน RViz เหมือนเดิม
    rviz_config_file = os.path.join(my_robot_pkg_dir, 'rviz', 'urdf_config.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        gazebo_launch,
        rviz_node
        # ## สังเกตว่าเราไม่ได้รัน slam_toolbox_node ในไฟล์นี้ ##
    ])