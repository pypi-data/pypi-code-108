#!/usr/bin/env python
# coding=utf-8

from setuptools import setup, find_packages
from myLabTools import __version__

setup(
    name='myLabTools',
    version=__version__,
    description=(
        '日常科研中使用到的工具'
    ),
    long_description=open('README.rst').read(),
    author='myqiang',
    author_email='mayq97@qq.com',
    maintainer='myqiang',
    maintainer_email='',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        "pymysql",
        "line_profiler",
        "pymongo",
        "elasticsearch",
        "sklearn",
        "transformers==4.4.0",
        "tqdm",
        "lxml",
        "flask"
    ]

)