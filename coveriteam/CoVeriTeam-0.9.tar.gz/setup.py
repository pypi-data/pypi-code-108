#!/usr/bin/env python3

# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import re
from setuptools import setup

with open("coveriteam/__init__.py") as inp:
    VERSION = re.search(r"^__version__\s*=\s*[\"\'](.*)[\"\']", inp.read(), re.M).group(
        1
    )

setup(
    name="CoVeriTeam",
    version=VERSION,
    author="Sudeep Kanav",
    description="CoVeriTeam: On-Demand Composition of Cooperative Verification Systems",
    url="https://gitlab.com/sosy-lab/software/coveriteam",
    packages=[
        "coveriteam",
        "coveriteam.interpreter",
        "coveriteam.language",
        "coveriteam.parser",
        "coveriteam.actors",
        "coveriteam.toolconfigs",
    ],
    package_data={"coveriteam": ["artifactlibrary/specifications/*.prp"]},
    install_requires=[
        "antlr4-python3-runtime>=4.8",
        "benchexec>=2.6",
        "requests>=2.24",
    ],
    setup_requires=[],
    tests_require=[],
    license="Apache-2.0",
    keywords="cooperative verification validation",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Testing",
    ],
    platforms=["Linux"],
    entry_points={"console_scripts": ["coveriteam = coveriteam.coveriteam:main"]},
)
