#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

with open("README.rst") as readme:
    long_description = readme.read()
    print(long_description)

setup(
    name="pxutil",
    version="0.0.12",
    description="Some handy Python tools",
    long_description=long_description,
    # long_description_content_type="text/markdown", # default is rst
    author="Peter Jiping Xie",
    author_email="peter.jp.xie@gmail.com",
    url="https://github.com/peterjpxie/pxutil.git",
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.5',
    entry_points = {
        'console_scripts': ['bashx=pxutil.cli:bashx_main'],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        # "Operating System :: MacOS", # Should work but not tested, better remove.
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",        
        "Topic :: Software Development :: Libraries",
    ],
)
