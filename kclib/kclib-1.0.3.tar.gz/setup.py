#!/usr/bin/env python3
__author__ = "gj"

from setuptools import setup,find_packages

setup(
	name = "kclib",
	version = "1.0.3",
	author = "gj",
	packages = find_packages(),
	license="GPLv3",
	python_requires = ">=3.6",
	install_requires=["xlrd"]
)
