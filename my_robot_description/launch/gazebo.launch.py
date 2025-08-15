import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
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
        Command(['xacro', ' ', urdf_path]),
        value_type=str
    )

    # Set environment variable to help Gazebo find your robot's resources (like meshes if you add them later)
    set_env_var_resources = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(pkg_share_dir, 'urdf')
    )

    # --- FIX APPLIED HERE ---
    # Launch Gazebo Sim, starting both the server and the GUI.
    # The '-s' (server-only) flag has been REMOVED to allow the GUI to launch.
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={
            # The world file 'empty.sdf' is now part of gz_args
            'gz_args': '-r -v 4 empty.sdf'
        }.items()
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content
        }]
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_robot',
            '-topic', 'robot_description',
            '-z', '0.1'
        ],
        output='screen'
    )

    # --- FIX APPLIED HERE ---
    # Create a bridge for LiDAR data with corrected syntax.
    # A closing bracket ']' has been added.
    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/model/my_robot/link/lidar_link/sensor/lidar/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan]'
        ],
        remappings=[
            ('/world/default/model/my_robot/link/lidar_link/sensor/lidar/scan', '/scan')
        ],
        output='screen'
    )

    laser_to_sonar_node = Node(
        package='my_robot_description',
        executable='laser_to_sonar',
        name='laser_to_sonar_node',
        output='screen',
        parameters=[
            {'pub_topic': '/range'},
            {'sub_topic': '/scan'}
        ]
    )

    return LaunchDescription([
        set_env_var_resources,
        gazebo_launch,
        robot_state_publisher,
        spawn_robot,
        lidar_bridge,
        laser_to_sonar_node
    ])
