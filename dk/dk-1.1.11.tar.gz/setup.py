#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The Datakortet Basic utilities package: `dk`.
"""

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.5
Topic :: Software Development :: Libraries
"""

import setuptools

version = '1.1.11'


setuptools.setup(
    name='dk',
    version=version,
    requires=[],
    install_requires=[
        'six',
        'ipaddr',  # from dk.iplist
    ],
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    license="LGPL",
    author='Bjorn Pettersen',
    author_email='bp@datakortet.no',
    url="http://www.github.com/datakortet/dk/",
    download_url='https://www.github.com/datakortet/dk',
    packages=setuptools.find_packages(exclude=['tests*']),
    zip_safe=False,
)
