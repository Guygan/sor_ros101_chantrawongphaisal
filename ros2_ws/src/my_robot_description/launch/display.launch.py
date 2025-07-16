from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():
    urdf_file = PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'urdf',
        'my_robot.urdf.xacro'
    ])

    rviz_config_file = PathJoinSubstitution([
        FindPackageShare('my_robot_description'),
        'rviz',
        'robot1.rviz'
    ])

    return LaunchDescription([
        DeclareLaunchArgument(
            name='rvizconfig',
            default_value=rviz_config_file,
            description='Full path to RVIZ config file'
        ),
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            parameters=[{
                'robot_description': Command(['xacro ', urdf_file])
            }]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', LaunchConfiguration('rvizconfig')],
            output='screen'
        )
    ])