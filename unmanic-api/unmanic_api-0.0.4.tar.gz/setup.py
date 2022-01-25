#!/usr/bin/env python
"""The setup script."""
import os
import re
import sys

from setuptools import setup

def get_version():
    """Get current version from code."""
    regex = r"__version__\s=\s\"(?P<version>[\d\.]+?)\""
    path = ("unmanic_api", "__version__.py")
    return re.search(regex, read(*path)).group("version")

def read(*parts):
    """Read file."""
    filename = os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts)
    sys.stdout.write(filename)
    with open(filename, encoding="utf-8", mode="rt") as fp:
        return fp.read()

with open("README.md") as readme_file:
    readme = readme_file.read()

# This call to setup() does all the work
setup(
    author="JeffResc",
    author_email="jeff@jeffresc.dev",
    classifiers=[
        "Framework :: AsyncIO",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="Asynchronous Python client for Unmanic.",
    include_package_data=True,
    version=get_version(),
    install_requires=list(val.strip() for val in open("requirements.txt")),
    keywords=["unmanic", "api", "async", "client"],
    license="MIT license",
    long_description_content_type="text/markdown",
    long_description=readme,
    name="unmanic_api",
    packages=["unmanic_api"],
    test_suite="tests",
    url="https://github.com/JeffResc/Unmanic-API",
)