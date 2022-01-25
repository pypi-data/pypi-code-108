#!usr/bin/python

# Copyright 2021 Deep Intelligence
# See LICENSE for details.

import io
from setuptools import setup, find_packages


def readme():
    with io.open('README.md', encoding='utf-8') as f:
        return f.read()


def requirements(filename):
    reqs = list()
    with io.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            reqs.append(line.strip())
    return reqs


setup(
    name='deepint',
    version='1.3.6',
    packages=find_packages(),
    url='https://deepint.net/',
    download_url='https://github.com/deepintdev/deepint-python-SDK/archive/master.zip',
    license='Copyright',
    author='Deep Intelligence',
    author_email='devs@deepint.net',
    description='deepint is a python package to work with Deep Intelligence in a more easy and intuitive way.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=requirements(filename='requirements.txt'),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries"
    ],
    python_requires='>=3',
    extras_require={
        "tests": requirements(filename='tests/requirements.txt'),
        "docs": requirements(filename='docs/requirements.txt')
    },
    keywords=', '.join([
        'deepint', 'Deep Intelligence', 'datawarehouse', 'analysis',
        'big data', 'IoT', 'Industry 4.0', 'Healthcare', 'smart cities'
    ]),
    project_urls={
        'Bug Reports': 'https://github.com/deepintdev/deepint-python-SDK/issues',
        'Source': 'https://github.com/deepintdev/deepint-python-SDK',
        'Documentation': 'https://deepint-python-sdk.readthedocs.io/en/latest/index.html'
    },
)
