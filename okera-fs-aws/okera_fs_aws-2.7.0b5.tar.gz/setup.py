#!/usr/bin/env python3
# Copyright Okera Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import ez_setup
ez_setup.use_setuptools()

import sys
from os.path import dirname, exists, join
import os
from setuptools import setup, find_packages, Extension
import versioneer  # noqa

package_version = versioneer.get_version()

def readme(version):
    with open('README.rst', 'r') as ip:
        readme = ip.read()
        return readme.replace('##OKERA_RELEASE_VERSION##', version)

reqs = [
    'jwt==0.5.4','requests==2.22.0', 'pytz>=3.0', 'urllib3==1.25.6',
    'pathlib' ]

setup(
    name='okera_fs_aws',
    maintainer='Okera Development Team',
    version=package_version,
    cmdclass=versioneer.get_cmdclass(),
    description='Python plugin supporting AWS CLI v1 for the Okera Data Access Service',
    long_description=readme(package_version),
    packages = find_packages(),
    install_requires=reqs,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    zip_safe=False)
