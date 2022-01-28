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
        name = 'wheel_axle',
        version = '0.0.1.dev20220128072321',
        description = 'Axle is Python wheel enhancement library',
        long_description = "# Axle - Python Wheel enhancement library\n\n\n## Problem\n\nPython `wheel` doesn't support symlinks.\n \n",
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

        url = 'https://github.com/karellen/axle',
        project_urls = {
            'Bug Tracker': 'https://github.com/karellen/axle/issues',
            'Documentation': 'https://github.com/karellen/axle/',
            'Source Code': 'https://github.com/karellen/axle/'
        },

        scripts = [],
        packages = ['wheel_axle.bdist_axle'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'distutils.commands': ['bdist_axle = wheel_axle.bdist_axle:BdistAxle']
        },
        data_files = [],
        package_data = {
            'wheel_axle/bdist_axle': ['LICENSE']
        },
        install_requires = [
            'wheel>=0.37.0',
            'wheel-axle-runtime'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.7',
        obsoletes = [],
    )
