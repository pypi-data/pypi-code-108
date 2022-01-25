#!/usr/bin/env python

#from distutils.core import setup

from setuptools import setup,find_packages

import os
here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.md'), 'r').read()
changelog = open(os.path.join(here, 'change.log'), 'r').read()


setup(name='ppss_pyramidutils',
      version='1.5.3',
      description='Simple utils to handle data from ini files in Pyramid for python 2.7 & 3',
      long_description=readme + "\n\n\n" + changelog,
      long_description_content_type="text/markdown",
      author='pdepmcp',
      author_email='pdepmcp@gmail.com',
      install_requires=['six'],
      keywords="pyramid module utils accelerator",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Operating System :: OS Independent",
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
      ],
      packages=find_packages()
     )
