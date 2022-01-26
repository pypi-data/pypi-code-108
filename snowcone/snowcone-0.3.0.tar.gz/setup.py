#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
from setuptools import find_packages
from setuptools import setup


this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="snowcone",
    author="Ismail Uddin",
    version="0.3.0",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="Useful utilities for Python",
    license="MIT license",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="array,snowcone,loaded",
    packages=find_packages(exclude=("tests")),
    test_suite="tests",
    url="https://www.github.com/ismailuddin/snowcone",
    zip_safe=False,
)
