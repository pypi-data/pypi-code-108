#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/26 12:06 下午
# @Author  : zhengyu.0985
# @FileName: setup.py
# @Software: PyCharm

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rolling-in-the-deep",
    version="0.0.3",
    author="RollingKing",
    author_email="386773780@qq.com",
    description="Python Project For QA Test",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/jason024/python_project",
    project_urls={
        "Bug Tracker": "https://gitee.com/jason024/python_project/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
