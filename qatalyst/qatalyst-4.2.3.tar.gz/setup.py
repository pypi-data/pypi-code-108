"""
(C) Quantum Computing Inc., 2020.

THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
The contents of this file may not be disclosed to third parties, copied
or duplicated in any form, in whole or in part, without the prior written
permission of the Copyright Holder.

Build the qci package.
"""
from setuptools import setup
import qatalyst.package_info as pi

# read the README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as fh:
    long_description = fh.read()

REQUIREMENTS = ['requests',
                'requests-toolbelt',
                'networkx',
                'scipy',
                'numpy',
                'pandas',
                'pyyaml',
                'amazon-braket-sdk',
                'markdown']

packages = ['qatalyst']
classifiers = [
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    ]

python_requires = '>=3.6'
name = 'qatalyst'

setup(
    name=name,
    version=pi.__version__,
    url="https://www.quantumcomputinginc.com/",
    packages=packages,
    package_dir={'qatalyst': 'qatalyst'},
    package_data={'qatalyst': ['./available_samplers.csv']},
    classifiers=classifiers,
    license='Apache 2.0',
    install_requires=REQUIREMENTS,
    python_requires=python_requires,
    author_email=pi.__authoremail__,
    author=pi.__author__,
    description=pi.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True
)
