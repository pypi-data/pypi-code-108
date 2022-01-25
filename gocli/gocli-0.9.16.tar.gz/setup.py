#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('./src/genomoncology/README.md') as readme_file:
    readme = readme_file.read()

history = ""

tests_require = [
    "flake8 == 3.7.9",
    "pytest-flake8 == 1.0.5",
    "black == 18.6b2",
    "ipython >= 6.4.0",
    "pytest == 5.4.2",
    "pytest-cov == 2.8.1",
    "pytest-mccabe == 1.0",
    "white == 0.1.2",
    "pytest-socket == 0.3.4",
    "pytest-asyncio == 0.12.0",
    "aioconsole == 0.1.16",
    "addict == 2.2.1",
    "requests >= 2.4",
]

setup(
    name="gocli",
    version='0.9.16',
    author="Ian Maurer",
    author_email='ian@genomoncology.com',

    packages=[
        "genomoncology",
        "genomoncology.kms",
        "genomoncology.cli",
        "genomoncology.parse",
        "genomoncology.pipeline",
        "genomoncology.pipeline.sinks",
        "genomoncology.pipeline.sources",
        "genomoncology.pipeline.sources.one_off_sources",
        "genomoncology.pipeline.transformers",
        "genomoncology.pipeline.transformers.tx",
        "gosdk",
        "govcf",
        "govcf.calculate_vaf",

    ],
    package_dir={
        '': 'src'
    },

    package_data={
        '': ["*.yaml", "*.bed", "*.txt", "*.tsv", "*.csv"]
    },

    include_package_data=True,

    tests_require=tests_require,
    install_requires=[
        "specd == 0.8.2",
        "backoff == 1.10.0",
        "click == 6.7",
        "structlog == 20.1.0",
        "colorama == 0.3.9",
        "pysam == 0.15.4",
        "ujson == 1.35",
        "intervaltree == 2.1.0",
        "glom == 20.5.0",
        "cytoolz == 0.10.1",
        "openpyxl == 3.0.3",
        "pygments == 2.2.0",
        "jsonschema[format] == 2.6.0",
        "flask == 1.0.2",
    ],

    setup_requires=[
        'pytest-runner',
    ],

    license="Proprietary",
    keywords='Bioinformatics HGVS VCF Clinical Trials Genomics',

    description="gocli",
    long_description="%s\n\n%s" % (readme, history),

    entry_points={
        'console_scripts': [
            'gocli=genomoncology.main:main',
        ],
    },

    classifiers=[
        'License :: Other/Proprietary License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
)
