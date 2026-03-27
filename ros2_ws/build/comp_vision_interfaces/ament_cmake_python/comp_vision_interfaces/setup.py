from setuptools import find_packages
from setuptools import setup

setup(
    name='comp_vision_interfaces',
    version='0.0.0',
    packages=find_packages(
        include=('comp_vision_interfaces', 'comp_vision_interfaces.*')),
)
