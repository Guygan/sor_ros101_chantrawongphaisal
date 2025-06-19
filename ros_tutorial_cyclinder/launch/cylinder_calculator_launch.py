from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='ros_tutorial_cyclinder',
            executable='cylinder_input',
            name='cylinder_input',
           
        ),
        Node(
            package='ros_tutorial_cyclinder',
            executable='cylinder_volume',
            name='cylinder_volume',
        )
    ])
