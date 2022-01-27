"""A setuptools based setup module.

See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
"""

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open
from os import path

# Always prefer setuptools over distutils
from setuptools import find_packages, setup


VERSION = "0.0.3"
NAME = "pygination"
AUTHOR = "Enerbit"
AUTHOR_EMAIL = "jdmoralesar@gmail.com"
DESCRIPTION = "Simple pagination for pydantic models and SQLAlchemy Query objects"
PROJECT_URL = "https://github.com/jdmoralesar/pygination"
DOWNLOAD_URL = "https://github.com/jdmoralesar/pygination/archive/refs/tags/0.0.1.tar.gz"

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
try:
    with open(path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,  
    long_description_content_type="text/markdown",
    url=PROJECT_URL,
    download_url=DOWNLOAD_URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="python pagination",
    packages=find_packages(include=[NAME, f"{NAME}.*"]),
    package_data={NAME: [f"{NAME}/py.typed"]},
    python_requires=">=3.7, <3.10",
    install_requires=["SQLAlchemy", "pydantic"],
)