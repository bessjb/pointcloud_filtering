from setuptools import find_packages, setup

package_name = 'pointcloud_filtering'

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
    maintainer='Bessen',
    maintainer_email='Bessen@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'pointcloud_processor = pointcloud_filtering.pointcloud_processor:main',
            'sample_code = pointcloud_filtering.sample_code:main'
        ],
    },
)
