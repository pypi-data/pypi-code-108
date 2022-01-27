#!/usr/bin/env python

from io import open
from setuptools import setup

"""
:authors: CazqevDev
:license: Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2021 CazqevDev
"""

version = '1.0.2'

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pycatbox',
    version=version,

    author='CazqevDev',
    author_email='nikprotect@protonmail.com',

    description=(
        u'Python module for uploading files to '
        u'CatBox (catbox.moe API wrapper)'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://n1kprotect.github.io/cazqev/',
    download_url='https://n1kprotect.github.io/cazqev/1',
    license='Apache License, Version 2.0, see LICENSE file',
    packages=['catbox'],
    install_requires=['requests'],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        ]
)