from setuptools import find_packages, setup

package_name = 'chess_common'

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
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='Shared utilities (repo paths) for the chess robot packages',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
)
