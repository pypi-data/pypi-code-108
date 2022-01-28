# SPDX-FileCopyrightText: 2019,2020 Freemelt AB
#
# SPDX-License-Identifier: Apache-2.0

# Built-in
import sys

# PyPI
import setuptools


with open("README.md", "r") as fh:
    description = fh.read()

sys.path.append('obplib')
from _version import __version__
sys.path.remove('obplib')

setuptools.setup(
    name='obplib',
    version=__version__,
    license="apache-2.0", 
    author="Freemelt AB",
    author_email="opensource@freemelt.com",
    description="A library for the creation of beam paths",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/freemelt/openmelt/obplib-python",
    download_url = "https://gitlab.com/freemelt/openmelt/obplib-python/-/archive/0.3.0/obplib-python-0.3.0.tar.gz",
    keywords = "obp openbeampath freemelt",
    packages=setuptools.find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'obpc=obplib.compiler.__main__:OBPC',
            'obpviewer=obplib.viewer.obpviewer:main'
        ]
    },
    install_requires=[
        'protobuf',
        'grpcio',
        # 'grpcio-tools',  # Only used in CI
        'svg.path==3.0',
        'click==7.0'
        ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],

)
