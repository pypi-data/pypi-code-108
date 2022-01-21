#!/usr/bin/env python

import setuptools
from guavacado import version_number

setuptools.setup(name='guavacado',
	version=version_number.guavacado_version,
	description='Simple Web API Hosting',
	author='Joshua Huseman',
	author_email='jhuseman@alumni.nd.edu',
	url='https://github.com/jhuseman/Guavacado',
	packages=['guavacado'],
)
