#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import setup, find_packages

NAME = 'search-string-overvaagning'
DESCRIPTION = 'SearchString is a custom implementation for searching strings'
URL = 'https://github.com/kaas-mulvad/search-string'
EMAIL = 'post@kaasogmulvad.dk'
AUTHOR = 'Søren Mulvad'
REQUIRES_PYTHON = '>=3.6.0'
REQUIRED = []
VERSION = '0.1.3'


DIR = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
try:
    with io.open(os.path.join(DIR, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

try:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(DIR, project_slug, 'version.py'), 'w') as f:
        f.write("__version__ = '{version}'\n".format(version=VERSION))
except Exception:
    pass

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    install_requires=REQUIRED,
    include_package_data=True,
    license='EULA',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
