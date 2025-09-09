import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler, TimerAction
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    """
    Launch Description to start Gazebo simulation, spawn the robot,
    run SLAM Toolbox, and RViz all in one command.
    """
    # ================== DIRECTORY AND FILE PATHS ==================
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    
    urdf_path = os.path.join(my_robot_pkg_dir, 'urdf', 'my_robot.urdf.xacro')
    bridge_config_path = os.path.join(my_robot_pkg_dir, 'config', 'gz_bridge.yaml')
    rviz_config_path = os.path.join(my_robot_pkg_dir, 'rviz', 'slam_view.rviz')
    ekf_config_path = os.path.join(my_robot_pkg_dir, 'config', 'ekf.yaml')

    # ======================= ROBOT DESCRIPTION =======================
    # Process the xacro file to generate the URDF robot description
    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]), 
        value_type=str
    )

    # ========================= GAZEBO SIMULATION =========================
    # Launch Gazebo Sim with an empty world
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # ========================== CORE ROS NODES ==========================
    # Publishes the robot's state and TF tree from the URDF
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': True, 
            'robot_description': robot_description_content
        }]
    )

    # Spawn the robot in Gazebo
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot'],
        output='screen'
    )
    
    # Extended Kalman Filter for sensor fusion (odometry)
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_path]
    )

    # Bridge between Gazebo and ROS 2 topics/services
    gz_ros_bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_ros_bridge',
        parameters=[{
            'config_file': bridge_config_path, 
            'use_sim_time': True
        }],
        output='screen'
    )

    # Your custom node to fix the scan frame_id
    frame_fixer_node = Node(
        package='my_robot_description',
        executable='frame_fixer',
        name='scan_frame_fixer',
        output='screen'
    )

    # Keyboard teleoperation node, launched in a new xterm window
    teleop_keyboard_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e' # This opens a new terminal for easy control
    )

    # ====================== SLAM AND VISUALIZATION ======================
    # SLAM Toolbox configuration parameters
    slam_params = {
        'use_sim_time': True,
        'odom_frame': 'odom',
        'map_frame': 'map',
        'base_frame': 'base_footprint',
        'scan_topic': '/scan_corrected', # Using the output of your frame_fixer
        'mode': 'mapping',
        'qos_scan': {
            'reliability': 'reliable',
            'history': 'keep_last',
            'depth': 5
        },
        'transform_timeout': 2.0,
        'minimum_travel_distance': 0.1,
        'minimum_travel_heading': 0.1,
        'max_laser_range': 10.0
    }
    
    # SLAM Toolbox Node
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params]
    )

    # RViz2 Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}]
    )

    # ======================= LAUNCH SEQUENCE HANDLER =======================
    # This is the key part: It waits for the robot to be spawned in Gazebo,
    # then waits for 5 seconds, and only then starts SLAM and RViz.
    # This ensures that all necessary transforms (TF) are available before SLAM starts.
    delayed_slam_and_rviz_starter = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_robot_node,
            on_exit=[
                TimerAction(
                    period=5.0,  # A short delay to allow all systems to stabilize
                    actions=[slam_toolbox_node, rviz_node]
                )
            ]
        )
    )

    # ========================= RETURN LAUNCH DESCRIPTION =========================
    return LaunchDescription([
        # Start Gazebo
        gazebo_launch,
        
        # Start core nodes
        robot_state_publisher_node,
        spawn_robot_node,
        robot_localization_node,
        gz_ros_bridge_node,
        frame_fixer_node,
        teleop_keyboard_node,
        
        # Use the event handler to start SLAM and RViz at the right time
        delayed_slam_and_rviz_starter
    ])
