# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2020-08-21 14:59:50
@LastEditTime: 2021-12-01 18:02:28
@LastEditors: HuangJianYi
@Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="seven_cloudapp_frame",
    version="1.0.11.99",
    author="seven",
    author_email="tech@gao7.com",
    description="seven cloudapp frame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://gitlab.tdtech.gao7.com/TaoBaoCloud/seven_cloudapp_frame.git",
    packages=find_packages(),
    install_requires=[
        "seven-framework >=1.0.108",
        "seven-top >=1.0.18",
        "asq==1.3",
        "emoji==1.6.1",
        "xmltodict==0.12.0",
        "requests-pkcs12==1.13",
        "mmh3==3.0.0"
    ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='~=3.4',
)