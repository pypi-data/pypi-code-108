# -*- coding: utf-8 -*-
"""Installer for the cpskin.diazotheme.spirit package."""

version = '0.1.47'

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='cpskin.diazotheme.spirit',
    version=version,
    description="Spirit theme for CPSkin",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='imio cpskin theme',
    author='IMIO',
    author_email='support@imio.be',
    url='https://github.com/IMIO/cpskin.diazotheme.spirit/',
    license='GPL',
    packages=find_packages(),
    namespace_packages=['cpskin', 'cpskin.diazotheme'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'cpskin.theme',
        'setuptools',
    ],
    extras_require={
    },
    entry_points="""
    """,
)
