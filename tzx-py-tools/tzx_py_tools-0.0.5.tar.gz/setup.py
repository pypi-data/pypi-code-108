#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   setup.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021/9/28 10:09     douly      1.0         setup
"""
# import lib

import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="tzx_py_tools",
  version="0.0.5",
  author="douly",
  author_email="mitiandameng@gmail.com",
  description="天智祥信息科技有限公司python工具包",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://fake.com/fake/fakeproject",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  ],
)