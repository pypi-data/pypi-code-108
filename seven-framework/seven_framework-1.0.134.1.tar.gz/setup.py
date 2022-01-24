# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-22 21:25:59
:LastEditTime: 2022-01-24 18:20:40
:LastEditors: ChenXiaolei
:Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="seven_framework",
    version="1.0.134.1",
    author="seven",
    author_email="tech@gao7.com",
    description="seven framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://gitlab.tdtech.gao7.com/python/seven_framework",
    packages=find_packages(),
    install_requires=[
        "elasticsearch <= 7.6.0",
        "requests >= 2.23.0",
        "PyMySQL >= 1.0.2",
        "python_dateutil >= 2.8.1",
        "redis >= 3.4.1",
        "pycryptodome >= 3.9.9",
        "tornado == 6.0.4",
        "bleach >= 3.1.5",
        "pycket >= 0.3.0",
        "ufile >= 3.2.2",
        "ks3sdk >= 1.0.16",
        "oss2 >= 2.13.1",
        "boto3 >= 1.20.37",
        "cos-python-sdk-v5 >= 1.9.0",
        "bce-python-sdk >= 0.8.61",
        "DBUtils == 1.3",
        "openpyxl >= 3.0.3",
        "xlwt >= 1.3.0",
        "xlrd >= 1.2.0",
        "xlutils >= 2.0.0",
        "qrcode >= 6.1",
        "Pillow >= 7.1.2",
        "threadpool >= 1.3.2",
        "filechunkio >= 1.8",
        "clickhouse-driver >= 0.2.0",
        "lxml >= 4.5.0"
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
