# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Thu Jul 29, 2021 at 02:39 AM +0200

import setuptools
import codecs
import os.path

from distutils.core import setup


###########
# Helpers #
###########

with open('README.md', 'r') as ld:
    long_description = ld.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


#########
# Setup #
#########

setup(
    name='pyTuplingUtils',
    version=get_version('pyTuplingUtils/__init__.py'),
    author='Yipeng Sun',
    author_email='syp@umd.edu',
    description='Utilities for ntuples, such as plotting and simple debugging, with the help of uproot',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/umd-lhcb/pyTuplingUtils',
    packages=setuptools.find_packages(),
    scripts=['bin/uidcommon', 'bin/uiddump', 'bin/plotbr', 'bin/plotbrdiff'],
    include_package_data=True,
    install_requires=[
        'uproot',
        'lz4',
        'matplotlib',
        'lark-parser',
        'mplhep'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent'
    ]
)
