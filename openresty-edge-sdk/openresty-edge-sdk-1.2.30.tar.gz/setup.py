#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement

from setuptools import setup, find_packages

import os
import sys

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

version = {}
with open(os.path.join(os.path.dirname(__file__),
          "edge2client/version.py")) as fp:
    exec(fp.read(), version)

long_description=""
with open('README.md', 'r') as fp:
    long_description = fp.read()

setup(

    name='openresty-edge-sdk',
    version=version['__version__'],
    description='OpenResty Edge Python SDK',
    platforms='Platform Independent',
    author='OpenResty Inc.',
    author_email='support@openresty.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=['openresty-edge-sdk', 'edge2client', 'python', 'sdk'],
    url="https://www.openresty.com",
    install_requires=['requests','urllib3'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(), # ["edge2client"],
)
