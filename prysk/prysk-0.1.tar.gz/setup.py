#!/usr/bin/env python
import inspect
from setuptools import setup

if __name__ == '__main__':
    setup(
        name='prysk',
        version='0.1',
        py_modules=['prysk'],
        author='Brodie Rao, Nicola Coretti',
        author_email='brodie@bitheap.org, nico.coretti@gmail.com',
        classifiers=[
            'Development Status :: 1 - Planning',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            ('License :: OSI Approved :: GNU General Public License v2 '
             'or later (GPLv2+)'),
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Unix Shell',
            'Topic :: Software Development :: Testing',
        ],
        description='Functional tests for command line applications',
        keywords='automatic functional test framework',
        license='GNU GPLv2 or any later version',
        long_description=inspect.cleandoc("""
        This is a fork of the well known cram tool 
        which can be found here https://bitheap.org/cram/
        """),
    )

