#!/usr/bin/env python

import os
from setuptools import setup, find_packages

ROOT = os.path.dirname(os.path.abspath(__file__))

meta = {}
with open(os.path.join(ROOT, "smartpay", "version.py"), encoding="utf-8") as f:
    exec(f.read(), meta)

setup(
    name="smartpay",
    version=meta["__version__"],
    author="Smartpay Co. Ltd.",
    author_email="uxe@smartpay.co",
    url="https://github.com/smartpay-co/sdk-python",
    description="Smartpay SDK Python",
    long_description=open(os.path.join(ROOT, "README.md")).read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["smartpay", "smartpay.schemas"],
    package_data={'': ['*.json']},
    install_requires=["jtd==0.1.1", "requests==2.25.1"],
)
