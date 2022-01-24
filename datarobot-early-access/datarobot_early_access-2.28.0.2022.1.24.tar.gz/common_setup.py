#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import re
import sys

from setuptools.command.test import test as TestCommand

DESCRIPTION_TEMPLATE = """
About {package_name}
============================
.. image:: https://img.shields.io/pypi/v/{package_name}.svg
   :target: {pypi_url_target}
.. image:: https://img.shields.io/pypi/pyversions/{package_name}.svg
.. image:: https://img.shields.io/pypi/status/{package_name}.svg

DataRobot is a client library for working with the `DataRobot`_ platform API. {extra_desc}

This package is released under the terms of the DataRobot Tool and Utility Agreement, which
can be found on our `Legal`_ page, along with our privacy policy and more.

Installation
=========================
Python {python_versions} are supported.
You must have a datarobot account.

::

   $ pip install {pip_package_name}

Usage
=========================
The library will look for a config file `~/.config/datarobot/drconfig.yaml` by default.
This is an example of what that config file should look like.

::

   token: your_token
   endpoint: https://app.datarobot.com/api/v2

Alternatively a global client can be set in the code.

::

   import datarobot as dr
   dr.Client(token='your_token', endpoint='https://app.datarobot.com/api/v2')

Alternatively environment variables can be used.

::

   export DATAROBOT_API_TOKEN='your_token'
   export DATAROBOT_ENDPOINT='https://app.datarobot.com/api/v2'

See `documentation`_ for example usage after configuring.

Tests
=========================
::

   $ py.test

.. _datarobot: http://datarobot.com
.. _documentation: {docs_link}
.. _legal: https://www.datarobot.com/legal/
"""


DEFAULT_CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ""

    def run_tests(self):
        import shlex

        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


with open("datarobot/_version.py") as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("Cannot find version information")

lint_require = [
    'black==19.10b0; python_version >= "3.6"',
    'isort==5.8; python_version >= "3.6"',
]

tests_require = [
    "mock==3.0.5",
    "pytest>=4.6,<5",  # 4.6 is last release supporting python2
    "pytest-cov",
    "responses>=0.9,<0.10",  # 0.10 changes the interface, will require test changes
]

_decorator_constraints = [
    'decorator<5; python_version=="2.7"',
]

dev_require = (
    tests_require
    + lint_require
    + _decorator_constraints
    + [
        # One of the packages in this list is depending on a broken version of docutils, causing
        # test-docs to fail, so we pin it here, despite this package doesn't really need it as such.
        #  See more: https://github.com/NVIDIAGameWorks/kaolin/issues/76
        "docutils==0.15.2",
        "flake8>=2.5.2,<3",
        "Sphinx==1.8.3",
        "sphinx_rtd_theme==0.1.9",
        "nbsphinx>=0.2.9,<1",
        "mistune==0.8.4",
        "nbconvert==5.3.1",
        "numpydoc>=0.6.0",
        "tox",
        "jupyter_contrib_nbextensions",
        "tornado<6.0",
        "jsonschema<=4.3.1",
    ]
)

example_require = _decorator_constraints + [
    "jupyter<=5.0",
    "fredapi==0.4.0",
    "matplotlib>=2.1.0",
    "seaborn<=0.8",
    "scikit-learn<=0.18.2",
    "wordcloud<=1.3.1",
    "colour<=0.1.4",
]

release_require = ["zest.releaser[recommended]==6.22.0"]

# The None-valued kwargs should be updated by the caller
common_setup_kwargs = dict(
    name=None,
    version=None,
    description="This client library is designed to support the DataRobot API.",
    author="datarobot",
    author_email="support@datarobot.com",
    maintainer="datarobot",
    maintainer_email="info@datarobot.com",
    url="http://datarobot.com",
    license="DataRobot Tool and Utility Agreement",
    packages=None,
    long_description=None,
    classifiers=None,
    install_requires=[
        "contextlib2>=0.5.5",
        "pandas>=0.15,<1.3.6",
        "pyyaml>=3.11",
        "requests>=2.21",
        "requests_toolbelt>=0.6",
        "trafaret>=0.7,<2.2,!=1.1.0",
        "urllib3>=1.23",
    ],
    tests_require=tests_require,
    extras_require={
        "dev": dev_require,
        "examples": example_require,
        "release": release_require,
        "lint": lint_require,
    },
    cmdclass={"test": PyTest},
)
