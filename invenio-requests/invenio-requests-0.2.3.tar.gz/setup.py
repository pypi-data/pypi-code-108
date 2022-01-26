# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generic and customizable requests."""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

tests_require = [
    "black>=20.8b1",
    "invenio-app>=1.3.2",
    "pytest-invenio>=1.4.2",
]

records_resources_version = ">=0.18.3,<0.19"

extras_require = {
    "docs": [
        "Sphinx>=4.2.0,<5.0",
    ],
    "elasticsearch6": [
        f"invenio-records-resources[elasticsearch6]{records_resources_version}"
    ],
    "elasticsearch7": [
        f"invenio-records-resources[elasticsearch7]{records_resources_version}"
    ],
    "mysql": [f"invenio-records-resources[mysql]{records_resources_version}"],
    "postgresql": [f"invenio-records-resources[postgresql]{records_resources_version}"],
    "sqlite": [f"invenio-records-resources[sqlite]{records_resources_version}"],
    "tests": tests_require,
}

extras_require["all"] = []
for name, reqs in extras_require.items():
    if name in (
        "elasticsearch6",
        "elasticsearch7",
        "mysql",
        "postgresql",
        "sqlite",
    ):
        continue
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=2.8",
]

install_requires = [
    "invenio-db>=1.0.9,<2.0",
    f"invenio-records-resources{records_resources_version}",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_requests", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio-requests",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio requests",
    license="MIT",
    author="CERN",
    author_email="info@inveniosoftware.org",
    url="https://github.com/inveniosoftware/invenio-requests",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "invenio_base.apps": [
            "invenio_requests = invenio_requests:InvenioRequests",
        ],
        "invenio_base.api_apps": [
            "invenio_requests = invenio_requests:InvenioRequests",
        ],
        "invenio_base.api_blueprints": [
            "invenio_requests = invenio_requests.views:create_requests_bp",
            "invenio_request_events = invenio_requests.views:create_request_events_bp"  # noqa
        ],
        "invenio_db.alembic": [
            "invenio_requests = invenio_requests:alembic",
        ],
        "invenio_db.models": [
            "invenio_requests = invenio_requests.records.models",
        ],
        "invenio_jsonschemas.schemas": [
            "jsonschemas = invenio_requests.records.jsonschemas",
        ],
        "invenio_search.mappings": [
            "requests = invenio_requests.records.mappings",
            "request_events = invenio_requests.records.mappings",
        ],
        "invenio_i18n.translations": [
            "messages = invenio_requests",
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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 1 - Planning",
    ],
)
