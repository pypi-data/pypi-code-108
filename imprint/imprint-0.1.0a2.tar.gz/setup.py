#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imprint: a program for creating documents from data and content templates
#
# Copyright (C) 2019  Joseph R. Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Author: Joseph Fox-Rabinovitz <jfoxrabinovitz at gmail dot com>
# Version: 13 Apr 2019: Initial Coding


"""
Setup script for building and installing imprint.
"""

from os.path import dirname, join
import sys

from setuptools import setup


DIST_NAME = 'imprint'

LICENSE = 'GNU Affero General Public License v3 or later (AGPLv3+)'
DESCRIPTION = 'Program for creating MS Word reports from data and content templates'

AUTHOR = 'Joseph R. Fox-Rabinovitz'
AUTHOR_EMAIL = 'jfoxrabinovitz@gmail.com'

MAINTAINER = 'Joseph R. Fox-Rabinovitz'
MAINTAINER_EMAIL = 'jfoxrabinovitz@gmail.com'

CLASSIFIERS = [
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Financial and Insurance Industry',
    'Intended Audience :: Healthcare Industry',
    'Intended Audience :: Legal Industry',
    'Intended Audience :: Manufacturing',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Other Audience',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Operating System :: Unix',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Office/Business',
    'Topic :: Text Processing :: Markup :: XML',
    'Topic :: Utilities',
]


COMMANDS = {}


try:
    from sphinx.setup_command import BuildDoc
    COMMANDS['build_sphinx'] = BuildDoc
except ImportError:
    pass


def import_file(name, location):
    """
    Imports the specified python file as a module, without explicitly
    registering it to `sys.modules`.

    While imprint uses Python 3 features, you are free to try to install
    it in a Python 2 environment.
    """
    if sys.version_info[0] == 2:
        # Python 2.7-
        from imp import load_source
        mod = load_source(name, location)
    elif sys.version_info < (3, 5, 0):
        # Python 3.4-
        from importlib.machinery import SourceFileLoader
        mod = SourceFileLoader(name, location).load_module()
    else:
        # Python 3.5+
        from importlib.util import spec_from_file_location, module_from_spec
        spec = spec_from_file_location(name, location)
        mod = module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod


def version_info():
    """
    Jump through some hoops to import version.py for the different
    versions of Python.

    https://stackoverflow.com/a/67692/2988730
    """
    location = join(dirname(__file__) or '.', 'src', 'imprint', 'version.py')
    mod = import_file('version', location)
    return mod.__version__


def long_description():
    """
    Reads in the README and CHANGELOG files, separated by two
    newlines.
    """
    with open('README.md') as readme, open('CHANGELOG') as changes:
        return '%s\n\n%s' % (readme.read(), changes.read())


if __name__ == '__main__':
    setup(
        name=DIST_NAME,
        version=version_info(),
        license=LICENSE,
        description=DESCRIPTION,
        long_description_content_type='text/markdown',
        long_description=long_description(),
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        classifiers=CLASSIFIERS,
        url='https://github.com/madphysicist/imprint',
        project_urls={
            'Bugs': 'https://github.com/madphysicist/imprint/issues',
            'Documentation': 'https://imprint.readthedocs.io/en/latest/',
        },
        packages=[
            'imprint',
            'imprint.core',
            'imprint.handlers',
            'imprint.handlers.figure',
            'imprint.handlers.table',
            'imprint.handlers.string',
            'imprint.tests',
        ],
        package_dir={'': 'src'},
        package_data={'imprint.tests': ['_resources/*.ipc']},
        install_requires=[
            'python-docx >= 0.8.5',
            'haggis[docx] >= 0.1a1',
        ],
        extras_require={
            'all': [
                'haggis[plot, latex, pdf] >= 0.1a1',
                'pandas >= 0.20'
            ],
            'latex': ['haggis[latex] >= 0.1a1'],
            'pdf': ['haggis[pdf] >= 0.1a1'],
        },
        provides=['imprint'],
        scripts=[
            'scripts/imprint', 'scripts/imprint.bat',
            'scripts/docx2xml', 'scripts/docx2xml.bat',
        ],
        data_files = [('', ['LICENSE', 'README.md', 'CHANGELOG'])],
        cmdclass=COMMANDS,
    )
