#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="delicate",
    version="1.0.2",
    author="Advent Group",
    author_email="development@adventgroup.net",
    description="Printing colored messages to the CLI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adventgroup/delicate",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
