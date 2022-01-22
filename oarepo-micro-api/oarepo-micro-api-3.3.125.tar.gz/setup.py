# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CESNET.
#
# OARepo Micro API is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OARepo REST API microservice"""

import os

from setuptools import find_packages, setup

readme = open('README.md').read()

packages = find_packages()

DATABASE = "postgresql"
OAREPO_VERSION = os.environ.get('OAREPO_VERSION', '3.3.121')

install_requires = [
    'oarepo~={version}'.format(version=OAREPO_VERSION),
    'oarepo-heartbeat>=1.0.2',
    'importlib_metadata',
    'uwsgi>=2.0',
    'uwsgi-tools>=1.1.1',
    'uwsgitop>=0.11',
    'wrapt>=1.12.1,<2.0.0'
]

tests_require = [
    'webtest',
    'pytest-pycodestyle',
    'pipdeptree'
]

setup_requires = [
    'pytest-runner>=2.7',
    'pytest-celery',
]

extras_require = {
    'tests': [
        *tests_require,
        'oarepo[tests]~={version}'.format(
            version=OAREPO_VERSION)
    ]
}

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('oarepo_micro_api', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
version = g['__version__']

setup(
    name='oarepo-micro-api',
    version=version,
    description=__doc__,
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    keywords='oarepo-micro-api Invenio',
    license='MIT',
    author='Miroslav Bauer @ CESNET',
    author_email='bauer@cesnet.cz',
    url='https://github.com/oarepo/oarepo-micro-api',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'oarepo = oarepo_micro_api.cli:cli'
        ],
        'invenio_config.module': [
            'oarepo_micro_api = oarepo_micro_api.config',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
