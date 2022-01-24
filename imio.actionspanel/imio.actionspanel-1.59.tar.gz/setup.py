# -*- coding: utf-8 -*-
"""Installer for the imio.actionspanel package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() + '\n' + open('CHANGES.rst').read() + '\n')

setup(
    name='imio.actionspanel',
    version='1.59',
    description="Actions panel",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='actions panel buttons',
    author='IMIO',
    author_email='dev@imio.be',
    url='https://github.com/imio/imio.actionspanel',
    download_url='https://pypi.org/project/imio.actionspanel',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['imio', ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'setuptools',
        'appy',
        'collective.fingerpointing',
        'imio.helpers',
        'imio.history>=1.17',
        'plone.api',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
