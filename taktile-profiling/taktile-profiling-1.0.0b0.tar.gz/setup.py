#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from pathlib import Path

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("docs/about/history.md") as history_file:
    history = history_file.read()


def strip_comments(l):
    return l.split("#", 1)[0].strip()


def _pip_requirement(req, *root):
    if req.startswith("-r "):
        _, path = req.split()
        return reqs(*root, *path.split("/"))
    return [req]


def _reqs(*f):
    path = (Path.cwd() / "reqs").joinpath(*f)
    with path.open() as fh:
        reqs = [strip_comments(l) for l in fh.readlines()]
        return [_pip_requirement(r, *f[:-1]) for r in reqs if r]


def reqs(*f):
    return [req for subreq in _reqs(*f) for req in subreq]


install_requires = reqs("base.txt")
test_requires = reqs("test.txt") + install_requires

setup(
    author="Taktile GmbH",
    author_email="devops@taktile.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="Taktile's Profiling Module",
    python_requires=">=3.7, <3.10",
    include_package_data=True,
    keywords="taktile-profiling",
    name="taktile-profiling",
    setup_requires=install_requires,
    install_requires=install_requires,
    packages=find_packages(),
    tests_require=test_requires,
    url="https://docs.taktile.com",
    version="1.0.0b0",
    zip_safe=False,
)
