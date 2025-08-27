# guygan/sor_ros101_chantrawongphaisal/sor_ros101_chantrawongphaisal-main/my_robot_description/launch/nav_display.launch.py

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    """
    ฟังก์ชันนี้ทำหน้าที่รวบรวม launch files ที่จำเป็นสำหรับ Navigation 2 (Nav2)
    ประกอบด้วยการเปิด Gazebo, ระบบของ Nav2, และ RViz.
    """

    # --- 1. กำหนด Path ไปยัง packages และไฟล์ที่ต้องการ ---
    # หาตำแหน่งของ package 'my_robot_description'
    my_robot_pkg_dir = get_package_share_directory('my_robot_description')
    # หาตำแหน่งของ package 'nav2_bringup' ซึ่งเป็นส่วนหนึ่งของ Nav2
    nav2_bringup_pkg_dir = get_package_share_directory('nav2_bringup')

    # --- 2. กำหนดค่า Configurations ที่จะใช้ ---
    # ตั้งค่าให้ Node ทั้งหมดใช้เวลาจำลอง (simulated time) จาก Gazebo
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    # Path ไปยังไฟล์พารามิเตอร์ของ Nav2 ที่เราตั้งค่าไว้
    params_file = os.path.join(my_robot_pkg_dir, 'config', 'nav2_params.yaml')
    # Path ไปยังไฟล์แผนที่ (map) ที่จะให้ Nav2 ใช้
    # map_file = os.path.join(my_robot_pkg_dir, 'maps', 'my_world.yaml') # หมายเหตุ: ในไฟล์ของคุณชื่อ my_map.yaml
    map_file = os.path.join(my_robot_pkg_dir, 'maps', 'my_map.yaml')


    # --- 3. เรียกใช้งาน Gazebo Simulation Launch File ---
    # เรียกใช้ gazebo.launch.py ที่เราได้สร้างและแก้ไขไว้ก่อนหน้านี้
    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(my_robot_pkg_dir, 'launch', 'gazebo.launch.py')
        )
    )

    # --- 4. เรียกใช้งาน Nav2 Bringup Launch File ---
    # นี่คือส่วนหลักในการเปิดระบบของ Nav2 ทั้งหมด (planner, controller, etc.)
    # โดยส่งพารามิเตอร์ที่จำเป็นเข้าไป เช่น use_sim_time, params_file, และ map
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_pkg_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'map': map_file,
        }.items()
    )

    # --- 5. รัน RViz2 Node ---
    # เปิดโปรแกรม RViz2 เพื่อแสดงภาพหุ่นยนต์, แผนที่, costmap, และเส้นทางของ Nav2
    # ใช้ไฟล์ configuration default ของ Nav2 เพื่อความสะดวก
    rviz_config_file = os.path.join(nav2_bringup_pkg_dir, 'rviz', 'nav2_default_view.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    # --- 6. คืนค่า LaunchDescription ---
    # รวบรวม launch files และ nodes ทั้งหมดเข้าด้วยกัน
    return LaunchDescription([
        gazebo_launch,
        nav2_bringup_launch,
        rviz_node
    ])