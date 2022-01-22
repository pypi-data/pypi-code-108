#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""dk-template - debugging django templates.
"""
import sys

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries
"""

import setuptools

version = '1.0.11'


setuptools.setup(
    name='dk-template',
    version=version,
    install_requires=[
        'django',
        'dk'
    ],
    author='Bjorn Pettersen',
    author_email='bp@datakortet.no',
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    packages=setuptools.find_packages(exclude=['tests']),
    zip_safe=False,
)
