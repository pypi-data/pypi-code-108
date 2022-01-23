#!/usr/bin/env python3

import re
import setuptools

with open("rpa_logger/_version.py", "r") as f:
    try:
        version = re.search(
            r"__version__\s*=\s*[\"']([^\"']+)[\"']",f.read()).group(1)
    except:
        raise RuntimeError('Version info not available')

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="rpa_logger",
    version=version,
    author="Toni Kangas",
    description="A simple python package for logging robotic process automation (RPA) progress.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kangasta/rpa_logger",
    project_urls={
        'Documentation': 'https://kangasta.github.io/rpa_logger/',
        'Source': 'https://github.com/kangasta/rpa_logger/',
        'Tracker': 'https://github.com/kangasta/rpa_logger/issues/',
    },
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
