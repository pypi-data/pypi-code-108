# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md") as f:
    README = f.read()


VERSION = "0.0.21"

setup(
    name="pymasmovil",
    version=VERSION,
    author="Coopdevs",
    author_email="gerard.funosas@somconnexio.coop",
    maintainer="Daniel Palomar, Pau Pérez, Gerard Funosas",
    url="https://gitlab.com/coopdevs/pymasmovil",
    description="Python client for the Más Móvil's B2B API",
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests", "docs")),
    include_package_data=True,
    zip_safe=False,
    install_requires=["requests"],
    test_suite="unittest2.collector",
    tests_require=["unittest2", "mock", "tox", "coverage", "httpretty"],
)
