#!/usr/bin/env python3

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
 
setup(
    name="curatorbin",
    version="1.2.4",
    description="install curator through pip and run it through python",
    url="https://github.com/evergreen-ci/curatorbin",
    license="SSPLv1",
    author="Harris Hoke",
    author_email="harris.hoke@mongodb.com",
    classifiers=[
        "Environment :: Console",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["curatorbin"],
    package_data={
        "curatorbin": [
            "arm/curator",
            "macos/curator",
            "macos-arm64/curator",
            "ubuntu/curator",
            "windows-64/curator.exe"
        ]
    }
)

