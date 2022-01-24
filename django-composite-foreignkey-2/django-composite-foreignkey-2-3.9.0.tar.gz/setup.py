#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import compositefk

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = compositefk.__version__

if sys.argv[-1] == 'publish':
    os.system('cd docs && make html')
    os.system('python setup.py sdist bdist_wheel upload')
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='django-composite-foreignkey-2',
    version=version,
    description="""composite foreignkey support for Django 4.x""",
    long_description=readme,
    author='Darius BERNARD',
    author_email='contact@xornot.fr',
    url='https://github.com/darkpixel/django-composite-foreignkey',
    packages=[
        'compositefk',
    ],
    include_package_data=True,
    install_requires=[
    ],
    license="GNU GENERAL PUBLIC LICENSE",
    zip_safe=False,
    keywords='django composite foreignkey',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Environment :: Web Environment',
        'Framework :: Django :: 4.0',
    ],
)
