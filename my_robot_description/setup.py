from setuptools import find_packages, setup
import os # เพิ่ม
from glob import glob # เพิ่ม

package_name = 'my_robot_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # เพิ่มบรรทัดเหล่านี้เพื่อติดตั้ง launch, urdf และ rviz files
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[py]*'))),
        (os.path.join('share', package_name, 'urdf'), glob(os.path.join('urdf', '*.urdf.xacro'))),
        (os.path.join('share', package_name, 'rviz'), glob(os.path.join('rviz', '*.rviz'))), # เพิ่มสำหรับ Rviz config
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='guygan',
    maintainer_email='guygan2002@gmail.com',
    description='Simple box robot for RViz demo',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)