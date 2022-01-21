# Copyright (c) 2019 AT&T Intellectual Property.
# Copyright (c) 2018-2019 Nokia.
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

#
# This source code is part of the near-RT RIC (RAN Intelligent Controller)
# platform project (RICP).
#

"""Setup script of Shared Data Layer (SDL) package."""

from os.path import dirname, abspath, join as path_join
from setuptools import setup, find_packages
from ricsdl import __version__

SETUP_DIR = abspath(dirname(__file__))


def _long_descr():
    """Yields the content of documentation files for the long description"""
    try:
        doc_path = path_join(SETUP_DIR, "README.md")
        with open(doc_path) as file:
            return file.read()
    except FileNotFoundError:  # this happens during unit testing, we don't need it
        return ""


setup(
    name="ricsdl",
    version=__version__,
    packages=find_packages(exclude=["tests.*", "tests"]),
    author="Timo Tietavainen",
    author_email='timo.tietavainen@nokia.com',
    license='Apache 2.0',
    description="Shared Data Layer (SDL) provides a high-speed interface to access shared storage",
    url="https://gerrit.o-ran-sc.org/r/admin/repos/ric-plt/sdlpy",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Telecommunications Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    keywords="RIC SDL",
    install_requires=[
        'setuptools',
        'redis==4.1.1',
        'hiredis==2.0.0'
    ],
    long_description=_long_descr(),
    long_description_content_type="text/markdown",
)
