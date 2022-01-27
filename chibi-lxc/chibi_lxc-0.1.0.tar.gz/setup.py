#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'chibi>=0.8.2', 'chibi_donkey>=1.0.0', 'chibi-command>=0.2.3',
    'python-hosts' ]

setup(
    author="dem4ply",
    author_email='dem4ply@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="definition of lxc containers using python",
    entry_points={
        'console_scripts': [
            'chibi_lxc=chibi_lxc.cli:main',
        ],
    },
    install_requires=requirements,
    license="WTFPL",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='chibi_lxc',
    name='chibi_lxc',
    packages=find_packages(include=['chibi_lxc', 'chibi_lxc.*']),
    url='https://github.com/dem4ply/chibi_lxc',
    version='0.1.0',
    zip_safe=False,
)
