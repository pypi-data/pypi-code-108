#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup, find_packages


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


gh_run_number = os.environ.get("BUILD_NUMBER", None)
build_number = None if gh_run_number is None or gh_run_number == "" else gh_run_number

version = '0.2.0'

with open('requirements.txt') as f:
    REQUIRES = f.readlines()

with open('test-requirements.txt') as f:
    TESTS_REQUIRES = f.readlines()

setup(
    name='airflow-gpg-plugin',
    version=f"{version}-{build_number}" if build_number else version,
    author='Tilak Patidar',
    author_email='tilakpatidar@gmail.com',
    maintainer='Tilak Patidar',
    maintainer_email='tilakpatidar@gmail.com',
    license='MIT',
    url='https://github.com/tilakpatidar/fibber-csv',
    description='Airflow plugin to work with GPG files.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    py_modules=['airflow_gpg_plugin'],
    python_requires='>=3.6.7',
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRES,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Security :: Cryptography',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required,
    entry_points={
        'airflow.plugins': [
            'airflow_gpg_plugin = airflow_gpg_plugin.plugin:AirflowGPGPlugin'
        ],
    },
)
