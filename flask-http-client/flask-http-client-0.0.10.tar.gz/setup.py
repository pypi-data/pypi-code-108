#!/usr/bin/env python
from setuptools import find_packages, setup

with open("README.rst", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="flask-http-client",
    version="0.0.10",
    description="HTTP client extension for Flask.",
    long_description=readme,
    author="codeif",
    author_email="me@codeif.com",
    url="https://github.com/codeif/flask-http-client",
    license="MIT",
    packages=find_packages(),
    install_requires=["Flask", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
