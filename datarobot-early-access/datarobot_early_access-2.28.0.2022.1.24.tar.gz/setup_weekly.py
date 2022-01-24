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
from datetime import datetime

from setuptools import find_packages, setup

from common_setup import common_setup_kwargs, DESCRIPTION_TEMPLATE, version

# weekly releases use a date for their "version"
version = version.split("b")[0]  # PyPI disallows 'b' unless followed by [.postN][.devN]
version += datetime.today().strftime(".%Y.%m.%d")

python_versions = "3.4 and higher"

# for weekly releases, we do not support python 2 any longer; default classifiers otherwise
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]

description = DESCRIPTION_TEMPLATE.format(
    package_name="datarobot_early_access",
    pypi_url_target="https://pypi.python.org/pypi/datarobot-early-access/",
    extra_desc=(
        'This package is the "early access" version of the client. **Do NOT use this package'
        " in production--you will expose yourself to risk of breaking changes and bugs.** For"
        " the most stable version, see the quarterly release on PyPI at"
        " https://pypi.org/project/datarobot/."
    ),
    python_versions=python_versions,
    pip_package_name="datarobot_early_access",
    docs_link="https://datarobot-public-api-client.readthedocs-hosted.com/en/early-access/",
)

packages = find_packages(exclude=["tests*"])

common_setup_kwargs.update(
    name="datarobot_early_access",
    version=version,
    packages=packages,
    long_description=description,
    classifiers=classifiers,
)

setup(**common_setup_kwargs)
