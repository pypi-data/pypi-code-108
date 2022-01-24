#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-bg-process",
    version="0.0.3",
    author="NoThlnG",
    author_email="hanguyl91@gmail.com",
    maintainer="NoThlnG",
    maintainer_email="hanguyl91@gmail.com",
    license="MIT",
    url="https://github.com/IndlgO/pytest-bg-process",
    description="Pytest plugin to initialize background process",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=["pytest_bg_process"],
    entry_points={"pytest11": ["bg-process = pytest_bg_process.plugin"]},
    python_requires=">=3.5",
    install_requires=["pytest>=3.5.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
)
