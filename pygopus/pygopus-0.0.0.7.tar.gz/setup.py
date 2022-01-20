import codecs
from setuptools import setup, find_packages
from pathlib import Path
import os

PYGOPUS_VERSION = "0.0.0.7"
DOWNLOAD_URL = ""


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [str(path.parent) for path in Path(package).glob("**/__init__.py")]


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join("..", path, filename))
    return paths


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, "r", "utf8") as f:
        return f.read()


extra_files = package_files("pygopus/bin")

setup(
    name="pygopus",
    packages=find_packages(),
    version=PYGOPUS_VERSION,
    description="Nothing but some dirty coding tricks make you happy with Excel automation.",
    long_description=read_file("README.md"),
    license="BSD-3",
    author="Hou",
    author_email="hhhoujue@gmail.com",
    url="",
    download_url=DOWNLOAD_URL,
    keywords=["excel", "automation"],
    install_requires=[
        "pydantic",
        "psutil",
        "httpx",
        "path",
    ],
    include_package_data=True,
    package_data={"pygopus": extra_files},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
)
