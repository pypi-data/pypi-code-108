#!/usr/bin/env python3
# coding: utf-8

import os
import re

from setuptools import setup, find_packages


# import volkanic; exit(1)
# DO NOT import your package from your setup.py


def read(filename):
    with open(filename, encoding='utf-8') as fin:
        return fin.read()


def _under_parent_dir(ref_path, *paths):
    parent_dir = os.path.dirname(ref_path)
    return os.path.join(parent_dir, *paths)


def find_version():
    path = _under_parent_dir(__file__, 'volkanic/__init__.py')
    regex = re.compile(
        r'''^__version__\s*=\s*('|"|'{3}|"{3})([.\w]+)\1\s*(#|$)''')
    with open(path) as fin:
        for line in fin:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            mat = regex.match(line)
            if mat:
                return mat.groups()[1]
    raise ValueError('__version__ definition not found')


config = {
    'name': 'volkanic',
    'version': find_version(),
    'description':
        "Interface with config files and shell prompts easily and elegantly",
    'keywords': '',
    'url': "https://github.com/frozflame/volkanic",
    'author': 'frozflame',
    'author_email': 'frozflame@outlook.com',
    'license': "GNU General Public License (GPL)",
    'packages': find_packages(include=['volkanic']),
    'zip_safe': False,
    'entry_points': {
        'console_scripts': ['volk = volkanic.__main__:registry']
    },
    'install_requires': read("requirements.txt"),
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],

    # ensure copy static file to runtime directory
    'include_package_data': True,
    'long_description': read('README.md'),
    'long_description_content_type': "text/markdown",
}

setup(**config)
