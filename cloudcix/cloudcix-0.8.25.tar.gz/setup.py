#!/usr/bin/env python

from setuptools import setup

with open('README.rst', 'r') as f:
    readme = f.read()

with open('requirements.txt', 'r') as f:
    requires = f.read().split('\n')

setup(
    name='cloudcix',
    version='0.8.25',
    description='Python3 bindings and utils for CloudCIX API.',
    long_description=readme,
    author='CloudCIX',
    author_email='developers@cloudcix.com',
    url='https://python-cloudcix.readthedocs.io/en/latest/',
    packages=[
        'cloudcix',
        'cloudcix.api',
    ],
    keywords=['cix', 'cloudcix', 'bindings', 'client', 'api'],
    install_requires=requires,
    package_data={'': ['LICENSE', 'README.rst']},
    package_dir={'cloudcix': 'cloudcix'},
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ])
