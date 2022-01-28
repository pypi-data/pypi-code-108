#!/usr/bin/python3
import setuptools
import re

with open("README.md") as f:
    description = f.read()

with open("arequest/arequest.py") as f:
    data = f.read()

version = re.findall(r'^__version__ = "(.*)"$', data, re.M)
if len(version) == 0:
    exit("Unknown version")
else:
    version = version[0]

setuptools.setup(
    name="arequest",
    version=version,
    author="p7e4",
    author_email="p7e4@qq.com",
    description="arequest is an async HTTP client for Python, with more customization.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/p7e4/arequest",
    packages=setuptools.find_packages(),
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires='>=3.8',
    install_requires=[
        "chardet",
        "h11"
    ]
)