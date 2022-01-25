#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'wheel-axle-runtime',
        version = '0.0.1.dev20220125044457',
        description = 'Axle Runtime is the runtime part of the Python Wheel enhancement library',
        long_description = '# Axle-Runtime - Python Wheel enhancement library\n\nThis is a companion to [bdist_axle](https://github.com/karellen/axle)\n\n## Problem\n\n## Solution\n\n### Invariants\n\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX',
            'Operating System :: POSIX :: Linux',
            'Topic :: System :: Archiving :: Packaging',
            'Topic :: Software Development :: Build Tools',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta'
        ],
        keywords = 'wheel packaging setuptools bdist_wheel symlink postinstall',

        author = 'Karellen, Inc.',
        author_email = 'supervisor@karellen.co',
        maintainer = 'Arcadiy Ivanov',
        maintainer_email = 'arcadiy@karellen.co',

        license = 'Apache License, Version 2.0',

        url = 'https://github.com/karellen/wheel-axle-runtime',
        project_urls = {
            'Bug Tracker': 'https://github.com/karellen/wheel-axle-runtime/issues',
            'Documentation': 'https://github.com/karellen/wheel-axle-runtime/',
            'Source Code': 'https://github.com/karellen/wheel-axle-runtime/'
        },

        scripts = [],
        packages = ['wheel_axle.runtime'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {
            'wheel_axle/runtime': ['LICENSE']
        },
        install_requires = [
            'filelock',
            'pip'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.7',
        obsoletes = [],
    )
