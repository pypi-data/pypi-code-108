###############################################################################
# (c) Copyright 2020-2021 CERN for the benefit of the LHCb Collaboration      #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from io import open
from os.path import abspath, dirname, join

from setuptools import find_packages, setup

here = abspath(dirname(__file__))

# Get the long description from the README file
with open(join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

package_data = []

setup(
    name="LbAPLocal",
    use_scm_version=True,
    description="Tool to locally run tests for AnalysisProductions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/lhcb-dpa/analysis-productions/lbaplocal",
    author="LHCb",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="LHCb AnalysisProductions DIRAC",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "click",
        "consolemd",
        "LbAPCommon~=0.5.9",
        "LbEnv",
        "LbDiracWrappers",
        "requests",
        "requests_kerberos",
        "setuptools",
    ],
    extras_require={
        "testing": [
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "pytest-timeout",
        ]
    },
    package_data={"LbAPLocal": package_data},
    entry_points={"console_scripts": ["lb-ap=LbAPLocal.cli:main"]},
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://gitlab.cern.ch/lhcb-dpa/analysis-productions/lbaplocal/-/issues",
        "Source": "https://gitlab.cern.ch/lhcb-dpa/analysis-productions/lbaplocal",
    },
)
