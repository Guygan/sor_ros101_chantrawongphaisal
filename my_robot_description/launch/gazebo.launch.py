import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_share_dir = get_package_share_directory('my_robot_description')
    urdf_path = os.path.join(pkg_share_dir, 'urdf', 'my_robot.urdf.xacro')
    bridge_config_path = os.path.join(pkg_share_dir, 'config', 'gz_bridge.yaml')

    # --- Arguments ---
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    use_sim_time = LaunchConfiguration('use_sim_time')

    # --- Robot Description ---
    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    # --- Nodes and Actions ---

    # 1. เรียกใช้ Gazebo Sim พร้อมกับ World พื้นฐาน (ว่างเปล่า)
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={
            'gz_args': '-r empty.sdf', # กลับมาใช้ empty.sdf
            'on_exit_shutdown': 'true',
        }.items()
    )

    # 2. เปิด Node 'robot_state_publisher'
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': robot_description_content
        }]
    )

    # 3. สร้าง (Spawn) หุ่นยนต์ใน Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'my_robot'],
        output='screen'
    )

    # 4. เปิด Node 'parameter_bridge'
    gz_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_ros_bridge',
        parameters=[{
            'use_sim_time': use_sim_time,
            'config_file': bridge_config_path
        }],
        output='screen'
    )

    # 5. เปิด Node ที่เราสร้างเอง
    laser_to_sonar_node = Node(
        package='my_robot_description',
        executable='laser_to_sonar',
        name='laser_to_sonar_node',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # 6. เพิ่ม Node สำหรับ teleop_twist_keyboard
    teleop_twist_keyboard_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e' # เปิด Node ในหน้าต่าง Terminal ใหม่
    )

    return LaunchDescription([
        use_sim_time_arg,
        gazebo_launch,
        robot_state_publisher,
        spawn_robot,
        gz_ros_bridge,
        laser_to_sonar_node,
        teleop_twist_keyboard_node
    ])

