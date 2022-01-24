from __future__ import absolute_import
from setuptools import setup

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'pynamematcher'))
from version import __version__

setup(
    name='PyNameMatcher',
    version=__version__,
    author='Constituent Voice LLC',
    author_email='chris.brown@constituentvoice.com',
    packages=['pynamematcher'],
    url='https://github.com/constituentvoice/PyNameMatcher',
    license='Apache',
    description='Simple library for matching first names with possible variations',
    long_description=open('README.rst').read(),
    install_requires=['Metaphone'],
    package_data={'pynamematcher': ['data/*.csv']},
    test_suite="tests",
    tests_require=['pytest']
)
