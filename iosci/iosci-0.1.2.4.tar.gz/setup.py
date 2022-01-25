#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import setuptools

version = "0.1.2.4"
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as readme:
    README = readme.read()
setuptools.setup(
    name="iosci",
    version=version,
    author="lichanghong",
    author_email="1211054926@qq.com",
    description="T解析podfile和批量修改组件版本号.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://hehuoya.com",
    install_requires=[
        'GitPython'
    ],
    packages=setuptools.find_packages(exclude=("iosci")),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ),
    exclude_package_data={'': ["iosci/test.py", "iosci/xcode/a.py","iosci/xcode/b.py"]}
)