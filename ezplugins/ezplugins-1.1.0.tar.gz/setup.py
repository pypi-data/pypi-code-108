#
# SPDX-License-Identifier: MIT
#
# Copyright (C) 2019-2021, AllWorldIT.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""EZPlugins setup."""

import re
from setuptools import find_packages, setup

main_py = open("ezplugins/__init__.py", "r", encoding="UTF-8").read()  # pylint: disable=consider-using-with
metadata = dict(re.findall('__([A-Z]+)__ = "([^"]+)"', main_py))

NAME = "ezplugins"
VERSION = metadata["VERSION"]

LONG_DESCRIPTION = open("README.md", "r", encoding="UTF-8").read()  # pylint: disable=consider-using-with

setup(
    name=NAME,
    version=VERSION,
    author="Nigel Kukard",
    author_email="nkukard@LBSD.net",
    description="EZPlugins is an easy to use plugin framework.",
    license="MIT",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://gitlab.oscdev.io/software/ezplugins",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development",
    ],
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests", "tests.*"]),
    command_options={
        "build_sphinx": {
            "project": ("setup.py", "EZPlugins"),
            "copyright": ("setup.py", "2019-2021, AllWorldIT"),
            "version": ("setup.py", VERSION),
            "source_dir": ("setup.py", "docs"),
        }
    },
)
