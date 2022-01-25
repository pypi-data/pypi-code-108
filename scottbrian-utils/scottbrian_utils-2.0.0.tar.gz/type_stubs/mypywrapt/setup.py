#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='wrapt-stubs',
    version='1.0.0',
    packages=['wrapt-stubs', 'adjust_src'],
    package_data={'wrapt-stubs': ['__init__.pyi', 'decorators.pyi']},
    entry_points={
        'console_scripts': [
            'adjust_src=adjust_src.adjust_src:main',
        ]}
)
