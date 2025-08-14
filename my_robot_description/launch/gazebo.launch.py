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
    # Get the share directory of your package
    pkg_share_dir = get_package_share_directory('my_robot_description')

    # Define the path to the single combined Xacro file
    urdf_path = os.path.join(pkg_share_dir, 'urdf', 'my_robot.urdf.xacro')

    # Create the full robot description from the main Xacro file
    robot_description_content = ParameterValue(
        Command(['xacro', ' ', urdf_path]),
        value_type=str
    )

    # Set environment variable for Gazebo resources (models, worlds)
    # This helps Gazebo find models defined in your URDF.
    set_env_var_resources = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=os.path.join(pkg_share_dir, 'urdf')
    )

    # --- KERNEL OF THE FIX ---
    # Open Gazebo Sim, starting both the server and the GUI.
    # We remove the '-s' (server-only) flag to allow the GUI to launch.
    # The gz_sim.launch.py script starts both server and client by default
    # when neither -s (server-only) nor -g (gui-only) is specified.
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        # The key change is removing '-s' from gz_args.
        # The ('gui', 'true') argument was also removed as it is not a valid
        # argument for gz_sim.launch.py and could cause confusion.
        launch_arguments={
            'gz_args': '-r -v 4'  # '-r' to run simulation on start, '-v 4' for verbosity
        }.items()
    )

    # Run robot_state_publisher node
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content
        }]
    )

    # Spawn the robot in Gazebo
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

    # Create a bridge for LiDAR data
    lidar_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/world/default/model/my_robot/link/lidar_link/sensor/lidar/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan'
        ],
        remappings=[
            ('/world/default/model/my_robot/link/lidar_link/sensor/lidar/scan', '/scan')
        ],
        output='screen'
    )

    # Node to convert LaserScan to Range (Sonar)
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
