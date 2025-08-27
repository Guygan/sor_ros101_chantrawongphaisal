import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    """
    ฟังก์ชันนี้จะถูกเรียกโดย ROS 2 launch system เพื่อสร้าง launch description.
    ทำหน้าที่ตั้งค่าและเปิดใช้งาน Nodes ที่จำเป็นสำหรับการจำลองหุ่นยนต์ใน Gazebo.
    """

    # --- 1. ค้นหาตำแหน่งของไฟล์และ Package ที่จำเป็น ---
    pkg_share_dir = get_package_share_directory('my_robot_description')
    urdf_path = os.path.join(pkg_share_dir, 'urdf', 'my_robot.urdf.xacro')

    # --- 2. ประมวลผลไฟล์ Xacro เป็น Robot Description ---
    robot_description_content = ParameterValue(
        Command(['xacro ', urdf_path]),
        value_type=str
    )

    # --- 3. เรียกใช้งาน Gazebo Simulation ---
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('ros_gz_sim'),
                'launch',
                'gz_sim.launch.py'
            ])
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items()
    )

    # --- 4. รัน Robot State Publisher ---
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True, 'robot_description': robot_description_content}]
    )

    # --- 5. Spawn หุ่นยนต์เข้าไปใน Gazebo ---
    robot_name = 'my_robot'
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', robot_name],
        output='screen'
    )

    # --- 6. สร้าง Bridge ระหว่าง ROS 2 และ Gazebo (ฉบับสมบูรณ์ที่สุด) ---
     # --- 6. สร้าง Bridge ระหว่าง ROS 2 และ Gazebo (ฉบับสมบูรณ์ที่สุด) ---
    gz_ros_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # --- ข้อมูลจาก Gazebo ส่งมายัง ROS ---
            f'/model/{robot_name}/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            f'/model/{robot_name}/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            
            # ✅ **แก้ไขล่าสุด:** ระบุ topic ของ Lidar ให้ถูกต้องตามชื่อเต็มใน Gazebo
            f'/world/empty/model/{robot_name}/link/lidar_link/sensor/lidar/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            
            f'/world/empty/model/{robot_name}/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',

            # --- คำสั่งจาก ROS ส่งไปยัง Gazebo ---
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
        ],
        remappings=[
            (f'/model/{robot_name}/tf', '/tf'),
            (f'/model/{robot_name}/odom', '/odom'),
            (f'/world/empty/model/{robot_name}/joint_state', '/joint_states'),
            
            # ✅ **แก้ไขล่าสุด:** เพิ่มการ remapping ให้ topic ของ Lidar
            # เพื่อให้ ROS 2 เห็นเป็น topic /scan ที่คุ้นเคย
            (f'/world/empty/model/{robot_name}/link/lidar_link/sensor/lidar/scan', '/scan'),
        ],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # --- 7. รัน Teleop Keyboard (สำหรับควบคุมหุ่นยนต์ด้วยคีย์บอร์ด) ---
    keyboard_teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_keyboard',
        output='screen',
        prefix='xterm -e' # เปิด Node นี้ใน terminal ใหม่
    )

    # --- 8. คืนค่า LaunchDescription ---
    return LaunchDescription([
        gazebo_launch,
        robot_state_publisher,
        spawn_robot,
        gz_ros_bridge,
        keyboard_teleop_node
    ])
