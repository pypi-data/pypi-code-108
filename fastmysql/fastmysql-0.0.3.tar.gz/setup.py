#!/usr/bin/env python3
# coding = utf8
"""
@ Author : ZeroSeeker
@ e-mail : zeroseeker@foxmail.com
@ GitHub : https://github.com/ZeroSeeker
@ Gitee : https://gitee.com/ZeroSeeker
"""
import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastmysql",
    version="0.0.3",
    author="ZeroSeeker",
    author_email="zeroseeker@foxmail.com",
    description="make it easy to use pymysql",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/ZeroSeeker/fastmysql",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'colorama==0.4.4',
        'envx==0.0.4',
        'numpy==1.22.0',
        'pandas==1.3.5',
        'PyMySQL==1.0.2',
        'python-dateutil==2.8.2',
        'pytz==2021.3',
        'showlog==0.0.6',
        'six==1.16.0',
        'tqdm==4.61.2'
    ]
)
