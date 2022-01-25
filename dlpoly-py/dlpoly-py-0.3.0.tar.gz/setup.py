#!/usr/bin/env python3

from setuptools import setup
from sphinx.setup_command import BuildDoc
import re

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open('dlpoly/__init__.py') as fd:
    version = re.search("__version__ = '(.*)'", fd.read()).group(1)

cmdclass = {'build_sphinx': BuildDoc}


install_requires = [
    'numpy>=1.5.0',
    'matplotlib>=2.0.0',
    'flake8',
    'ruamel.yaml',
    'coverage',
    'pytest',
    'pytest-cov',
    'tox',
    'sphinx'
]

name = "dlpoly-py"

setup(name='dlpoly-py',
      version = version,
      description = 'dlpoly4 python module for file manipulation',
      long_description = long_description,
      author = 'Alin M Elena, Jacob Wilkins',
      author_email = 'alinm.elena@gmail.com, jacob.wilkins@oerc.ox.ac.uk',
      url = 'https://gitlab.com/drFaustroll/dlpoly-py',
      packages = ['dlpoly'],
      license = 'BSD-3',
      install_requires=install_requires,
      classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
      ],
      command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'source_dir': ('setup.py', 'doc')}},
      )
