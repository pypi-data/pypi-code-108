# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "pytest-invenio>=1.4.0",
]

invenio_search_version = ">=1.4.0,<1.5.0"
invenio_db_version = ">=1.0.9,<1.1.0"

extras_require = {
    "elasticsearch7": [f"invenio-search[elasticsearch7]{invenio_search_version}"],
    "mysql": [f"invenio-db[mysql,versioning]{invenio_db_version}"],
    "postgresql": [f"invenio-db[postgresql,versioning]{invenio_db_version}"],
    "sqlite": [f"invenio-db[versioning]{invenio_db_version}"],
    "docs": [
        "Sphinx>=4",
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for reqs in extras_require.values():
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=2.8",
]

install_requires = [
    "Flask-WebpackExt>=1.0.0",
    "invenio-app-rdm>=7.0.0",
    "Flask>=2.0.2",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_theme_tuw", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-theme-tuw",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio theme tuw",
    license="MIT",
    author="TU Wien",
    author_email="tudata@tuwien.ac.at",
    url="https://gitlab.tuwien.ac.at/fairdata/invenio-theme-tuw",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "invenio_base.apps": [
            "invenio_theme_tuw = invenio_theme_tuw:InvenioThemeTUW",
        ],
        "invenio_assets.webpack": [
            "invenio_theme_tuw_theme = invenio_theme_tuw.webpack:theme",
        ],
        "invenio_config.module": [
            "invenio_theme_tuw = invenio_theme_tuw.config",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
    ],
)
