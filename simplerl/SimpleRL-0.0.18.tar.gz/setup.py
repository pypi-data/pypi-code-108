#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 14:47:03 2021

@author: hemerson
"""

from setuptools import setup, find_packages

VERSION = '0.0.18' 
DESCRIPTION = 'SimpleRL'
LONG_DESCRIPTION = 'A package containing several lightweight reinforcement learning environments'

# Setting up
setup(
        name="SimpleRL", 
        version=VERSION,
        author="Harry Emerson",
        author_email="emersonharry8@gmail.com",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
        	"numpy>=1.21.4",
        	"pygame>=2.1.0",
		"setuptools>=58.0.4",
		"imageio>=2.13.3",
                "scipy>=1.7.3"
            ],        
        keywords=['reinforcement learning', 'environment'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
