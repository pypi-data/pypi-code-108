from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

VERSION = '0.1.0'

setup(
    name='Triangle-Msh-To-Voronoi',  # package name
    version=VERSION,  # package version
    description='三角形网格转为泰森多边形',  # package description
    packages=find_packages(),
    zip_safe=False,
    url="https://github.com/Littlestar007/TriangleToVoronoi",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)