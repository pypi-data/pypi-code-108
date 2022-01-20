# -*- coding: utf-8 -*-
"""
Created on Thus Jan 20 14:37:04 2022

@author: avik_
"""

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cosine_similarity", # Replace with your own username
    version="0.1.0",
    author="Avik Das",
    author_email="avik_das_2017@cba.isb.edu",
    description="This package help you to calculate similarity of texts.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=2.0",
)