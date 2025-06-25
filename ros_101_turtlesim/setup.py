from setuptools import find_packages, setup
import os
from glob import glob


package_name = 'ros_101_turtlesim'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='guygan',
    maintainer_email='guygan2002@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
   entry_points={
    'console_scripts': [
        'turtle_square = ros_101_turtlesim.square_turtle:main',
        'turtle_guide_to_xy = ros_101_turtlesim.turtle_guide_to_xy:main',
    ],
},


)
