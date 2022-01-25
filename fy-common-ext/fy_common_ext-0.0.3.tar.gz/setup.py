#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Just for editable install."""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fy_common_ext",
    version="0.0.3",
    author="fyabc",
    author_email="fyabc95@gmail.com",
    description="Some common extensions of Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fyabc/SmallTools/tree/master/Python/fy_common_ext",
    # project_urls={
    #     "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    # },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
