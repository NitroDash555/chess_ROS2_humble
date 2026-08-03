from setuptools import find_packages, setup

package_name = 'comp_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=[
    'setuptools',
    'numpy<2.0',
    'opencv-python-headless<4.11.0',
    'ultralytics',
    'shapely',
    'python-dotenv',
    'python-chess',
    'pillow',
    'matplotlib',
    ],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': ['comp_vision = comp_vision.comp_vision:main'
        ],
    },
    package_data={
        'comp_vision': [
            'chess_vision/assets/models/*.pt',
            'chess_vision/*.jpg',  # если нужны тестовые фото
        ],
    },
    include_package_data=True,
)
