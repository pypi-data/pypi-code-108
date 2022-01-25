#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='adjust_sphinx',
    version='1.0.0',
    packages=['adjust_sphinx'],
    entry_points={
        'console_scripts': [
            'adjust_sphinx=adjust_sphinx.adjust_sphinx:main',
        ],
    })
