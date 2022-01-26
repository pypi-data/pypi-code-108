#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

import os
parent_path = os.path.relpath('.')
path_to_file = parent_path+'/README.md'
with open(path_to_file, 'r') as f:
    long_description = f.read()

setuptools.setup(
    name="b2bTools",
    version="3.0.1b5",
    author="Wim Vranken",
    author_email="Wim.Vranken@vub.be",
    description="bio2Byte software suite to predict protein biophysical properties from their amino-acid sequences",
    license="OSI Approved :: GNU General Public License v3 (GPLv3)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    maintainer="Jose Gavalda-Garcia, Adrian Diaz, Wim Vranken",
    maintainer_email="jose.gavalda.garcia@vub.be, adrian.diaz@vub.be, wim.vranken@vub.be",
    url="https://bio2byte.be",
    project_urls={
        # "Bug Tracker": "https://bitbucket.org/bio2byte/b2btools/issues",
        "Documentation": "https://bio2byte.be/b2btools/package-documentation",
        # "Source": "https://bitbucket.org/bio2byte/b2btools/",
        "HTML interface" : "https://bio2byte.be/b2btools"
    },
    packages=setuptools.find_packages(exclude=("**/test/**",)),
    include_package_data=True,
    keywords="b2bTools,biology,bioinformatics,bio-informatics,fasta,proteins,protein-folding",
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Development Status :: 5 - Production/Stable"
    ],

    python_requires='==3.7.*',

    install_requires=[
        'future==0.18.2',
        'joblib==1.0.1',
        'networkx==2.6.2',
        'numpy==1.21.2',
        'Pillow==8.3.1',
        'pomegranate==0.14.4',
        'PyYAML==5.4.1',
        # 'scikit-learn==0.20.4',
        'scikit-learn>=1.0.1',
        'scipy==1.7.1',
        'six==1.16.0',
        'threadpoolctl==2.2.0',
        'torch==1.2.0',
        'torchvision==0.4.0'
    ]
)
