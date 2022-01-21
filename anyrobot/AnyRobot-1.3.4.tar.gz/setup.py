#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__)) + os.path.sep + 'README.rst'

with open(here, "r") as f:
  long_description = f.read()
setup(name='AnyRobot',
      version='1.3.4',
      description='This is a data service module that solves test data problems.',
      long_description=long_description,
      author='Evan.hu',
      author_email='1056212287@qq.com',
      url='https://mp.weixin.qq.com/s/v6FS96ifCoMvp_rwrhzhKw',
      install_requires=[],
      license='BSD License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
    )