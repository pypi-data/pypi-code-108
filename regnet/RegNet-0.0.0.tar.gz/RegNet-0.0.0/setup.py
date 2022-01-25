#!/usr/bin/env python
"""
# Author: Lei Xiong
# Contact: jsxlei@gmail.com
# File Name: setup.py
# Created Time : Tue 25 Jan 2022 11:20:34 PM CST
# Description:

"""

from setuptools import setup, find_packages

setup(
    name='RegNet',
    version="0.0.0",
    packages=find_packages(),
    description='',

    author='Lei Xiong',
    author_email='jsxlei@gmail.com',
    url='https://github.com/jsxlei/RegNet',
    python_requires='>3.6.0',
    license='MIT',

    classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 3.7',
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Microsoft :: Windows',
      'Operating System :: POSIX :: Linux',
      'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    )