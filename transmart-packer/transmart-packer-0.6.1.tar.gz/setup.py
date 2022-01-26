#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup

if sys.version_info < (3, 7):
    sys.exit(
        'Python < 3.7 is not supported. You are using Python {}.{}.'.format(
            sys.version_info[0], sys.version_info[1])
    )

here = os.path.abspath(os.path.dirname(__file__))

# To update the package version number, edit packer/__version__.py
version = {}
with open(os.path.join(here, 'packer', '__version__.py')) as f:
    exec(f.read(), version)

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt', 'r') as f:
    required_packages = f.read().splitlines()

setup(
    name='transmart-packer',
    version=version['__version__'],
    description="Data transformation jobs for TranSMART",
    long_description=readme + '\n\n',
    author="Jochem Bijlard",
    author_email='jochem@thehyve.nl',
    url='https://github.com/thehyve/transmart-packer',
    packages=[
        'packer',
        'packer.jobs',
        'packer.table_transformations'
    ],
    entry_points={
        'console_scripts': ['transmart-packer=packer.main:main'],
    },
    include_package_data=True,
    license="GNU General Public License v3 or later",
    zip_safe=False,
    keywords=[
        'transmart-packer',
        'transmart'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10'
    ],
    test_suite='tests',
    python_requires='>=3.7.0',
    install_requires=required_packages,
    setup_requires=[
        # dependency for `python setup.py test`
        'pytest-runner',
        # dependencies for `python setup.py build_sphinx`
        'sphinx',
        'sphinx_rtd_theme',
        'recommonmark',
        # dependency for `python setup.py bdist_wheel`
        'wheel'
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'pycodestyle',
    ],
    extras_require={
        'dev':  ['prospector[with_pyroma]', 'pygments', 'yapf', 'isort'],
    }
)
