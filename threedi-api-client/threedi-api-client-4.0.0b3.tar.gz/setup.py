#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import codecs
import re
import os
import pathlib

here = os.path.abspath(os.path.dirname(__file__))


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def get_version():
    # Edited from https://packaging.python.org/guides/single-sourcing-package-version/
    init_path = pathlib.Path(__file__).parent / "threedi_api_client/__init__.py"
    for line in init_path.open("r").readlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


requirements = [
    'certifi>=2019.3.9',
    'urllib3>=1.15',
    'pyjwt>=1.7.1',
    'six>=1.10',
    'python-dateutil',
]

aio_requirements = ['aiohttp>=3.6.3', "aiofiles"]

# Note: mock contains a backport of AsyncMock
test_requirements = ["pytest", "pytest-asyncio", "mock"]


setup(
    author="Lars Claussen",
    author_email='lars.claussen@nelen-schuurmans.nl',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    description="client for the threedi API",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='threedi-api-client',
    name='threedi-api-client',
    packages=find_packages(
        include=[
            'openapi_client', 'openapi_client.*',
            'threedi_api_client', 'threedi_api_client.*'
        ]
    ),
    python_requires='>=3.6',
    extras_require={
        "aio": aio_requirements,
        "test": test_requirements,
    },
    test_suite='tests',
    url='https://github.com/nens/threedi-api-client',
    version=get_version(),
    zip_safe=False,
)
