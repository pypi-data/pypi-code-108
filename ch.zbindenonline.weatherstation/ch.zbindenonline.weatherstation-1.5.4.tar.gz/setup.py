# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="ch.zbindenonline.weatherstation",
    version="1.5.4",
    description="Collects data from tinkerforge outdoor weather station and saves it to sqlite database.",
    license="MIT",
    author="Patrick Zbinden",
    packages=find_packages(),
    install_requires=['requests', 'click', 'tinkerforge'],
    entry_points={
        'console_scripts': [
            'saveMeasures=ch.zbindenonline.weatherstation.saveMeasures:main',
            'publishMeasures=ch.zbindenonline.weatherstation.publishMeasures:main',
            'publishPictures=ch.zbindenonline.weatherstation.publishPictures:main'
        ]
    },
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
