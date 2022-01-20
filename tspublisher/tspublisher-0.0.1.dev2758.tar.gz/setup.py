#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='tspublisher',
    version='0.0.1.dev2758',
    license='GNU General Public License',
    description='Touch Surgery publishing tools',
    long_description=read('README.md'),
    author='TS Content Squad',
    author_email='admin@touchsurgery.com',
    url='https://www.touchsurgery.com/jobs',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    keywords=[],
    install_requires=[
        'requests',
        'ruamel.yaml',
        'gitpython',
        'pycryptodome',
        'yolk',
        'pillow',
        'future',
        'polib',
        'six',
        'yolk',
        'ftrack-python-api'
    ],
    extras_require={
        'development': [
            'codecov',
            'flake8',
            'mock',
            'pytest',
            'pytest-cov',
            'pytest-pep8',
        ]
    },
    entry_points={
        'console_scripts': [
            'tspub = publisher.cli:main',
        ],
        'gui_scripts': [
            'tschanedit = publisher.gui:channel_editor',
        ]
    }
)
