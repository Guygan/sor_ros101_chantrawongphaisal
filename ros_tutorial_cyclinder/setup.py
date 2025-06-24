import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'ros_tutorial_cyclinder'  # หรือแก้เป็น 'ros_tutorial_cylinder' ถ้าชื่อจริงเป็นแบบนี้

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
         ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='guygan',
    maintainer_email='guygan2002@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cylinder_input = ros_tutorial_cyclinder.cylinder_input:main',
            'cylinder_squared = ros_tutorial_cyclinder.cylinder_subscriber:main',
            'cylinder_volume = ros_tutorial_cyclinder.cylinder_volume:main',
            'cylinder_weight = ros_tutorial_cyclinder.cylinder_weight:main',
        ],
    },
)
