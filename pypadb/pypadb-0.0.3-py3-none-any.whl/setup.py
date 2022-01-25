#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

__author__ = 'ChenzDNA'

from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(name="pypadb",
      version="0.0.3",
      description='Interaction with database in a simple way',
      author="ChenzDNA",
      author_email='1007324849@qq.com',
      url='https://github.com/ChenzDNA/pypa',
      packages=find_packages(),
      long_description=long_description,
      long_description_content_type="text/markdown",
      license="Apache-2.0",
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Apache Software License",
          "Operating System :: OS Independent"],
      python_requires='>=3.5',
      install_requires=[
          "DBUtils>=2.0.2",
          "pydantic>=1.8.2",
          "PyMySQL>=1.0.2",
      ]
      )
