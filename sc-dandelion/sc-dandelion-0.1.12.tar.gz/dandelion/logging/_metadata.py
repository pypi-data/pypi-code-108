#!/usr/bin/env python
# @Author: Kelvin
# @Date:   2021-04-03 16:46:13
# @Last Modified by:   Kelvin
# @Last Modified time: 2021-07-18 17:55:22

try:
    from setuptools_scm import get_version
    __version__ = get_version(root="../..",
                              relative_to=__file__,
                              git_describe_command = "git describe --dirty --tags --long --match v*.*.*").split('+')[0]
except:
    from .version import __version__
__author__ = "Zewen Kelvin Tuong"
__email__ = "kt16@sanger.ac.uk"
__classifiers__ = [
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: R",
    "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
]
