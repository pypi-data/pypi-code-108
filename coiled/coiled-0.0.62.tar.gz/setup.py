#!/usr/bin/env python

from os.path import exists

import versioneer
from pkg_resources import parse_requirements
from setuptools import find_packages, setup

setup(
    name="coiled",
    url="https://coiled.io",
    maintainer="Coiled",
    maintainer_email="info@coiled.io",
    version=versioneer.get_version(),  # type: ignore
    cmdclass=versioneer.get_cmdclass(),  # type: ignore
    description="",
    packages=find_packages(),
    include_package_data=True,
    long_description=(open("README.md").read() if exists("README.md") else ""),
    long_description_content_type="text/markdown",
    zip_safe=False,
    install_requires=[
        str(requirement)
        for requirement in parse_requirements(open("requirements.txt").read())
    ],
    entry_points={"console_scripts": ["coiled=coiled.cli.core:cli"]},
    python_requires=">=3.7, <3.10.0",
)
