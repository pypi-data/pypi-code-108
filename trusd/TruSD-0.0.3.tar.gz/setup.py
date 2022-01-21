#!/usr/bin/env python3

import setuptools

long_description = open('README.md').read()

setuptools.setup(
    name='TruSD',
    version='0.0.3',
    author='Mathias Bockwoldt',
    author_email='mathias.bockwoldt@gmail.com',
    description='TruSD co-infers selection coefficients and genetic drift from allele trajectories using a maximum-likelihood framework.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mathiasbockwoldt/TruSD',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': [
                                    'trusd = trusd.cli:main',
                                    'trusd-sim = trusd.cli:simulate',
                                    'trusd-plot = trusd.cli:plot'
                                    ]},
    install_requires=[
        'numpy>=1.15.1',
        'scipy>=0.16.0',
        'matplotlib>=3.1.1',
    ],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    python_requires='>=3.6',
)
