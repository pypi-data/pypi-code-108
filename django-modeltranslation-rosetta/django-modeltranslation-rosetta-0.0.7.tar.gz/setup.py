# !/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

version = "0.0.7"

if sys.argv[1] == "bumpversion":
    print("bumpversion")
    try:
        part = sys.argv[2]
    except IndexError:
        part = "patch"

    os.system("bumpversion --config-file setup.cfg %s" % part)
    sys.exit()

__doc__ = ""

project_name = "django-modeltranslation-rosetta"
app_name = "modeltranslation_rosetta"

ROOT = os.path.dirname(__file__)


def read(fname):
    return open(os.path.join(ROOT, fname)).read()


setup(
    name=project_name,
    version=version,
    description=__doc__,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Apkawa/%s" % project_name,
    author="Apkawa",
    author_email="apkawa@gmail.com",
    packages=[package for package in find_packages() if package.startswith(app_name)],
    python_requires=">=3.7, <4",
    install_requires=[
        "six",
        "Django>=1.11",
        "tablib",
        "openpyxl>=2.6.0",
        "Babel>=2.9.1",
        "inflection",
        "lxml",
        "defusedxml",
        "django-modeltranslation",
    ],
    zip_safe=False,
    include_package_data=True,
    keywords=["django"],
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
