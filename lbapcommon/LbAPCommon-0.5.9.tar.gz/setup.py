###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
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

package_data = ["validators/logs/data/known_messages.yaml"]

setup(
    name="LbAPCommon",
    use_scm_version=True,
    description="Common utilities used by LHCb DPA WP2 related software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/lhcb-dpa/analysis-productions/LbAPCommon",
    author="LHCb",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="LHCb HEP CERN",
    packages=find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.6",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "strictyaml",
        "jinja2",
        "lxml",
        "pyyaml",
        "setuptools",
        "boost-histogram",
        "hist",
        "requests",
        "requests-kerberos",
        "uproot>=4.0.0",
        "awkward>=1.0.0",
        "matplotlib",
    ],
    extras_require={"testing": ["pytest", "pytest-cov", "pytest-timeout"]},
    package_data={"LbAPCommon": package_data},
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://gitlab.cern.ch/lhcb-dpa/analysis-productions/LbAPCommon/issues",
        "Source": "https://gitlab.cern.ch/lhcb-dpa/analysis-productions/LbAPCommon",
    },
)
