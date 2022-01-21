#!/usr/bin/env python
import sys
import archer_ballistics

from setuptools import setup, find_packages


extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True
    extra['convert_2to3_doctests'] = ['README.md']

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
    ]

KEYWORDS = 'async wialon remote api wrapper'

setup(name='py_archer_ballistics',
      version=archer_ballistics.__version__,
      description="""Archer Ballistics Calculator""",
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      author=archer_ballistics.__author__,
      url='https://github.com/o-murphy/py_archer_ballistics',
      packages=find_packages(),
      download_url='http://pypi.python.org/pypi/py_archer_ballistics/',
      classifiers=CLASSIFIERS,
      keywords=KEYWORDS,
      zip_safe=True,
      install_requires=[],
      py_modules=['archer_ballistics']
      )
