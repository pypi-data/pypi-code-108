#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from setuptools import setup
import sys

# In this way, we are sure we are getting
# the installer's version of the library
# not the system's one
setupDir = os.path.dirname(__file__)
sys.path.insert(0, setupDir)

from log2tg_ng import __version__ as log2tg_ng_version

def long_description():
	this_dir = os.path.abspath(os.path.dirname(__file__))
	with open(os.path.join(this_dir, 'README.md'), encoding='utf-8') as f:
		return f.read()


def requirements():
	requirements_list = list()
	with open('requirements.txt') as pc_requirements:
		for install in pc_requirements:
			requirements_list.append(install.strip())
	return requirements_list


setup(
	name='logging2telegram-ng',
	version=log2tg_ng_version,
	packages=['log2tg_ng'],
	url='https://github.com/jmfernandez/loging2telegram-ng',
	author='jmfernandez',
	license='Apache License, Version 2.0, see LICENSE file',
	description='Telegram logging handler (next generation)',
	long_description=long_description(),
	long_description_content_type='text/markdown',
	install_requires=requirements(),
	classifiers=[
		'License :: OSI Approved :: Apache Software License',
		'Operating System :: OS Independent',
		'Environment :: Console',
		'Development Status :: 3 - Alpha',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: Implementation :: PyPy',
	]
)
