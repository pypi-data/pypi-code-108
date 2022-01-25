#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "0.1.1"

long_description = """Supercellmap is a tool to map primitive cell quantities in primitive cell into supercells."""

setup(
    name='supercellmap',
    version=__version__,
    description='Supercellmap is a tool to map primitive cell quantities in primitive cell into supercells.',
    long_description=long_description,
    author='Xu He',
    author_email='mailhexu@gmail.com',
    license='BSD-2-clause',
    packages=find_packages(),
    scripts=[
    ],
    install_requires=['numpy', 'ase'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: BSD License',
    ],
    python_requires='>=3.6',
)
