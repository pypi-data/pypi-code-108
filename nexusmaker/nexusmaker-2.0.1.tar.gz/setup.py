#!/usr/bin/env python
from setuptools import setup, find_packages

__version__ = "2.0.1"

setup(
    name='nexusmaker',
    version=__version__,
    description="nexusmaker - Nexus file maker for language phylogenies",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/SimonGreenhill/NexusMaker',
    author='Simon J. Greenhill',
    author_email='simon@simon.net.nz',
    license="BSD-2-Clause",
    zip_safe=True,
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='language-phylogenies phylolinguistics',
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.7',
    install_requires=[
        'python-nexus>=2.6.0',
        'pycldf>=1.24.0',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=5',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
)
