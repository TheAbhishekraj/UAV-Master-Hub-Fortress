from setuptools import setup
import os
from glob import glob

package_name = 'agri_hexacopter'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name, package_name + '.flight_levels'],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include launch files
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        # Include world files
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Abhishek',
    maintainer_email='abhishek@todo.todo',
    description='Autonomous Thermal-Imaging Hexacopter for Bihar Smallholder Farms',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_control = agri_hexacopter.mission_control:main',
            'real_takeoff = agri_hexacopter.real_takeoff:main',
            'level1_basic_takeoff = agri_hexacopter.flight_levels.level1_basic_takeoff:main',
            'level2_survey_grid = agri_hexacopter.flight_levels.level2_survey_grid:main',
            'thermal_monitor = agri_hexacopter.thermal_monitor:main',
        ],
    },
)
