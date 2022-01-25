#!/usr/bin/env python3
"""parallel_docker_build."""

import sys
import importlib.util
from setuptools import setup, find_packages
import site

# Enables --editable install with --user
# https://github.com/pypa/pip/issues/7953
site.ENABLE_USER_SITE = "--user" in sys.argv[1:]


_spec = importlib.util.spec_from_file_location(
    "__metadata__", "./parallel_docker_build/__metadata__.py"
)
METADATA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(METADATA)

# Check python version
MIN_VERSION = "3.6"
if sys.version_info < tuple(int(i) for i in MIN_VERSION.split(".")):
    raise Exception(
        "{} doesn't support python<{}".format(METADATA.__name__, MIN_VERSION)
    )

with open("README.md", "r") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name=METADATA.__name__,
    version=METADATA.__version__,
    description=METADATA.__description__,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=METADATA.__url__,
    download_url=f"{METADATA.__url__}/-/tags",
    author=METADATA.__author__,
    # author_email=METADATA.__email__,
    maintainer=METADATA.__author__,
    # maintainer_email=METADATA.__email__,
    classifiers=METADATA.__classifiers__,
    platforms="any",
    packages=find_packages(where="."),
    include_package_data=True,
    python_requires=">={}".format(MIN_VERSION),
    install_requires=["docker", "yamale"],
    tests_require=[
        "pytest",
        "pytest-cov",
        "bump2version",
        "pre-commit",
    ],
    keywords="automation docker continuous-deployment",
    license=METADATA.__license__,
    entry_points={
        "console_scripts": [
            "parallel-docker-build = " "parallel_docker_build.cli:main",
        ],
    },
)
