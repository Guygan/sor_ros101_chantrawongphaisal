import os
from glob import glob
from setuptools import setup, find_packages # เพิ่ม find_packages

package_name = 'my_robot_description'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(include=[package_name, package_name + '.*']), # บอกให้ setuptools ค้นหาและติดตั้ง Python package
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # รวมไฟล์ launch ทั้งหมด
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.py'))),
        # รวมไฟล์ xacro ทั้งหมด
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.xacro'))),
        # รวมไฟล์ RViz config (ถ้ามี)
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', '*.rviz'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='guygan',
    maintainer_email='guygan2002@gmail.com',
    description='Robot with RViz and Gazebo using ROS 2',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'laser_to_sonar = my_robot_description.laser_to_sonar_node:main' # entry_point นี้ถูกต้องแล้ว
        ],
    },
)
