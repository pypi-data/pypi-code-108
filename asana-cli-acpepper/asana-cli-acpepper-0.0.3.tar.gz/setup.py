#!/usr/bin/env python3

from setuptools import setup, find_packages

readme = open('README.md').read()
exec(open('asana_cli/version.py').read())

setup(
    name='asana-cli-acpepper',
    version=__version__,
    description='CLI for asana.',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Al Johri',
    author_email='al.johri@gmail.com',
    maintainer='Andrew Pepper',
    maintainer_email="andrewpepper96@gmail.com",
    url='https://github.com/AlJohri/asana-cli',
    license='MIT',
    packages=find_packages(),
    install_requires=['click', 'asana',],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'asana=asana_cli.cli:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ]
)
