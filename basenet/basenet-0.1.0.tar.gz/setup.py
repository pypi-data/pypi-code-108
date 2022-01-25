#!/usr/bin/env/python

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fp:
    readme = fp.read()
setup(
    name='basenet',
    author='Ben Johnson',
    author_email='bkj.322@gmail.com',
    classifiers=[],
    description='pytorch training tools',
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=['basenet', 'pytorch', 'training'],
    license='Apache-2.0',
    packages=find_packages(),
    version="0.1.0"
)
