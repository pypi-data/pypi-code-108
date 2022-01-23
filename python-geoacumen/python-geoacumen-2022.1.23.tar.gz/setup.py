import re
import subprocess

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

import os

with open("geoacumen/__init__.py") as f:
    version = re.search(r'__version__ = "(.*?)"', f.read()).group(1)


def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname), "r") as fp:
            return fp.read().strip()
    except IOError:
        return ""


subprocess.call(
    [
        "wget",
        "-O",
        "geoacumen/db/Geoacumen-Country.mmdb",
        "https://github.com/geoacumen/geoacumen-country/raw/master/Geoacumen-Country.mmdb",
    ]
)


setup(
    name="python-geoacumen",
    version=version,
    author="Kevin Chung",
    author_email="kchung@nyu.edu",
    license="Apache 2.0",
    description="Library to access/distribute Geoacumen IP databases",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[],
    install_requires=["maxminddb==1.5.4"],
    packages=find_packages(include=["geoacumen", "geoacumen.*"]),
    include_package_data=True,
)
