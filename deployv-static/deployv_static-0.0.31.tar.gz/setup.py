#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = open('requirements.txt').readlines()
test_requirements = open('test-requirements.txt').readlines()

setup(
    name='deployv_static',
    version='0.0.31',
    description="DeployV static files: Dockerfiles, json, configs, templates",
    long_description=readme + '\n\n' + history,
    author="Vauxoo",
    author_email='info@vauxoo.com',
    url='https://github.com/Vauxoo/deployv-static',
    packages=[
        'deployv_static',
    ],
    package_dir={'deployv_static':
                 'deployv_static'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='deployv-static',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
