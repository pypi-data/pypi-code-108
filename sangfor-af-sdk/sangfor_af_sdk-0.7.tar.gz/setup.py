'''
Author: 饕餮
Date: 2021-12-23 21:23:03
version: 
LastEditors: 饕餮
LastEditTime: 2022-01-19 17:23:52
Description: setup
'''
from __future__ import print_function
from setuptools import setup,find_packages
import sys

setup(
    name="sangfor_af_sdk",
    version="0.7",
    author="spensercai",
    author_email="spensercai@gmail.com",
    description="Sangfor AF SDK",
    long_description="Sangfor AF SDK",
    license="MIT",
    url="https://github.com/SpenserCai/Sangfor-AF-SDK",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[

    ],
    install_requires=[

    ],
    zip_safe=True,

)