#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
from time import localtime,strftime
vi="5.0.6"
day=1
local=strftime(f"%Y%m%d",localtime())
setup(
    name='allenlib',
    version=f"{vi}",
    description=(
        'allenlib'
    ),
    long_description=open('README.md',encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author='刘雨桐',
    author_email='UNKNOWN',
    maintainer='刘雨桐',
    maintainer_email='UNKNOWN',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'requests','pygame'
    ]
)