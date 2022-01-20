#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of PyZenKit package.
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2015 Honza Mach <honza.mach.ml@gmail.com>
# Use of this package is governed by the MIT license, see LICENSE file.
#
# This project was initially written for personal use of the original author. Later
# it was developed much further and used for project of author`s employer.
#-------------------------------------------------------------------------------

# Resources:
#   https://packaging.python.org/en/latest/
#   https://python-packaging.readthedocs.io/en/latest/index.html

import sys
import os

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open

#
# Import local version of pynspect library, so that we can insert correct version
# number into documentation.
#
sys.path.insert(0, os.path.abspath('.'))
import pyzenkit

here = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'pyzenkit',
    version = pyzenkit.__version__,
    description = 'Python 3 script and daemon toolkit',
    long_description = long_description,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
    ],
    keywords = 'library console script daemon',
    url = 'https://github.com/honzamach/pyzenkit',
    author = 'Honza Mach',
    author_email = 'honza.mach.ml@gmail.com',
    license = 'MIT',
    packages = find_packages(),
    test_suite = 'nose.collector',
    tests_require = [
        'nose'
    ],
    install_requires=[
        'python-dotenv',
        'jsonschema',
        'pydgets'
    ],
    include_package_data = True,
    zip_safe = False
)
