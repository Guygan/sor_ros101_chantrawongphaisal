import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    slam_toolbox_pkg_dir = get_package_share_directory('slam_toolbox')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(my_robot_pkg_dir, 'launch', 'gazebo.launch.py')
        )
    )

    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
          os.path.join(slam_toolbox_pkg_dir, 'config', 'mapper_params_online_async.yaml'),
          {'use_sim_time': True}
        ],
        remappings=[
            ('/scan', 'scan'),
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('/map', 'map')
        ]
    )

    rviz_config_file = os.path.join(my_robot_pkg_dir, 'rviz', 'urdf_config.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        gazebo_launch,
        slam_toolbox_node,
        rviz_node
    ])
