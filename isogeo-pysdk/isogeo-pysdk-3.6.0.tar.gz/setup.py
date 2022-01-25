# -*- coding: utf-8 -*-
#! python3  # noqa E265

"""
    Setup script to package Isogeo PySDK Python module

    see: https://github.com/isogeo/isogeo-api-py-minsdk/
"""

# ############################################################################
# ########## Libraries #############
# ##################################

# standard library
import pathlib

from setuptools import find_packages, setup

# package metadata
from isogeo_pysdk import __about__

# SETUP ######################################################################

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# setup metadata
setup(
    # meta
    name="isogeo-pysdk",
    version=__about__.__version__,
    author=__about__.__author__,
    author_email=__about__.__email__,
    description=__about__.__summary__,
    long_description=README,
    long_description_content_type="text/markdown",
    keywords="GIS metadata INSPIRE Isogeo API REST geographical data ISO19139",
    license="LGPL3",
    url=__about__.__uri__,
    project_urls={
        "Docs": "https://isogeo-api-pysdk.readthedocs.io/",
        "Bug Reports": "{}issues/".format(__about__.__uri__),
        "Source": __about__.__uri__,
        "Isogeo API": "http://help.isogeo.com/api/",
    },
    # dependencies
    install_requires=["requests>=2.20.0", "requests-oauthlib>=1.2.0"],
    extras_require={
        "dev": ["black", "python-dotenv"],
        "test": ["pytest", "pytest-cov"],
    },
    python_requires=">=3.7, <4",
    # packaging
    packages=find_packages(
        exclude=["contrib", "docs", "*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    include_package_data=True,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
