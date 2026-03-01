from setuptools import setup

package_name = 'agri_bot_missions'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Abhishek',
    maintainer_email='abhishek@example.com',
    description='Autonomous missions for the Bihar Farm Digital Twin',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'level1_hover = agri_bot_missions.level1_hover:main',
            'level2_box = agri_bot_missions.level2_box:main',
            'level3_survey = agri_bot_missions.level3_survey:main',
        ],
    },
)