#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys

from setuptools import find_packages, setup
from helpers import __version__

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
	README = readme.read()

setup(
	name='tonicapp-helpers',
	version=__version__,
    packages=find_packages(),
	include_package_data=True,
	license='MIT License',
	description='Toolbox with general functions and models to avoid repetition.',
	long_description=README,
    long_description_content_type='text/markdown',
	author='tonicapp',
	author_email='web@tonicapp.com',
    install_requires = [
        'firebase-admin==4.3.0',
        'user-agents==2.2.0'
    ],
	classifiers=[
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
