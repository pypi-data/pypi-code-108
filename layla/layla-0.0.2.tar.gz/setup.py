#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 25 00:35:22 2022

@author: Mohammad Asim
"""

from setuptools import setup, find_packages

setup(
        name="layla", 
        version="0.0.2",
        author="Mohammad Asim",
        author_email="asim.98.12.26@gmail.com",
        description='Deep learning package for automating experimentation, prototyping and tuning',
        long_description=open('README.md').read(),
        packages=find_packages(),
        license='LICENSE.txt',
        url = "https://asimbluemoon@bitbucket.org/laylaelectric/ml.git",
        install_requires=["tensorflow >= 2.3"],
        keywords=['python', 'layla'],
        classifiers= [
            "Development Status :: 1 - Planning",
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent"
        ]
)