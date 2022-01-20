#!/usr/bin/env python3

import re
from setuptools import setup


# Get the version number from __init__.py

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open("phadd/phadd.py").read(),
    re.M,
).group(1)


# Import pypandoc to convert the readme

try:
     import pypandoc
     long_description = pypandoc.convert("README.md", "rst")
except ImportError:
    long_description = ""
         

# setup configuration

setup(
    name="parallel-hadd",
    version=version,
    description = "A python package to hadd files in parallel",
    long_description=long_description,
    author="Mohamed Elashri",
    author_email="muhammadelashri@gmail.com",
    url="https://github.com/MohamedElashri/hadd-parallel",
    license="MIT",
    platforms=["any"],
    packages=["phadd"],
    entry_points={
        "console_scripts": [
            "phadd = phadd.phadd:main"
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License ",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=[
        "hadd",
        "ROOT",
        "ROOT histogram",
        "Physics",
        "ROOT CERN",
        "Histograms",
    ],
    setup_requires=[
        "pypandoc",
        "pytest-runner",
    ],
    tests_require=["pytest"],
    python_requires=">=3.6, <4",
)
      
