#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from pathlib import Path

from setuptools import find_packages, setup  # type: ignore

with open("README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()


def strip_comments(line):
    return line.split("#", 1)[0].strip()


def _pip_requirement(req, *root):
    if req.startswith("-r "):
        _, path = req.split()
        return reqs(*root, *path.split("/"))
    return [req]


def _reqs(*f):
    path = (Path.cwd() / "reqs").joinpath(*f)
    with path.open() as fh:
        reqs = [strip_comments(line) for line in fh.readlines()]
        return [_pip_requirement(r, *f[:-1]) for r in reqs if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


install_requires = reqs("base.txt")
test_requires = reqs("test.txt") + install_requires

setup(
    author="Taktile GmbH",
    author_email="devops@taktile.com",
    license="Apache License 2.0",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Taktile's CLI ",
    python_requires=">=3.7, <3.10",
    entry_points={"console_scripts": ["tktl=tktl.main:cli",],},
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="taktile-cli",
    name="taktile-cli",
    setup_requires=install_requires,
    install_requires=install_requires,
    test_suite="tests",
    packages=find_packages(),
    tests_require=test_requires,
    url="https://docs.taktile.com",
    version="1.0.0b0",
    zip_safe=False,
)
