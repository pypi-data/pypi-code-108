#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    path = os.path.join(package, "__init__.py")
    init_py = open(path, "r", encoding="utf8").read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_long_description():
    """
    Return the README.
    """
    return open("README.md", "r", encoding="utf8").read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, "__init__.py"))
    ]


minimal_requirements = [
    "PyYAML>=5.1",
]

extra_requirements = [
]

setup(
    name="sls.python",
    url="https://github.com/Om3rr/pyverless",
    license="BSD",
    description="Serverless for translator for pythonistas",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Omer Shacham",
    author_email="omer20sh@gmail.com",
    packages=get_packages("uvicorn"),
    python_requires=">=3.6",
    install_requires=minimal_requirements,
    extras_require={"standard": extra_requirements},
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points="""
    [console_scripts]
    pyverless=pyverless.gen:main
    pyls=pyverless.gen:main
    """,
    project_urls={
        "Funding": "https://github.com/sponsors/om3rr",
        "Source": "https://github.com/Om3rr/pyverless",
        "Changelog": "https://github.com/Om3rr/pyverless/blob/master/CHANGELOG.md",
    },
)
