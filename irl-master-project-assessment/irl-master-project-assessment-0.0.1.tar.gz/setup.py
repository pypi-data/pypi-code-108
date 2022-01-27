from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Car Race Simulation Package'
LONG_DESCRIPTION = 'A program that simulates the functionality of three models of cars on an Infinitely Long Road(IRL):' \
                   'namely FastCar, SlowCar, and UniqueCar'

setup(
    name="irl-master-project-assessment",
    version=VERSION,
    author="Jeremy Plaza",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pytest'],
    keywords=['python', 'irl', 'project assessment', 'simple car simulation'],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"
    ]
)
