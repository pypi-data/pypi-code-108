#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'boto3', 'pydantic>1.8.0']

test_requirements = ['pytest>=3', ]

setup(
    author="Martijn Meijer",
    author_email='tech@itsallcode.nl',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Create APIs by combining models and state machines",
    entry_points={
        'console_scripts': [
            'api_machine=api_machine.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='python_api_machine',
    name='python_api_machine',
    packages=find_packages(
        include=['api_machine', 'api_machine.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/itsallcode-nl/python_api_machine',
    version='0.2.5',
    zip_safe=False,
)
