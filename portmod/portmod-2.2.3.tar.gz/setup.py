#!/usr/bin/env python

# Copyright 2019-2020 Portmod Authors
# Distributed under the terms of the GNU General Public License v3


import os

from setuptools import find_packages, setup
from setuptools_rust import Binding, RustExtension

with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as file:
    long_description = file.read()


setup(
    name="portmod",
    author="Portmod Authors",
    author_email="incoming+portmod-portmod-9660349-issue-@incoming.gitlab.com",
    description="A CLI package manager for mods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPLv3",
    url="https://gitlab.com/portmod/portmod",
    download_url="https://gitlab.com/portmod/portmod/-/releases",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    rust_extensions=[
        RustExtension("portmodlib.portmod", binding=Binding.PyO3, strip=True)
    ],
    zip_safe=False,
    entry_points=(
        {
            "console_scripts": [
                "inquisitor = portmod._cli.inquisitor:main",
                "portmod= portmod._cli.main:main",
            ]
        }
    ),
    python_requires=">=3.6",
    install_requires=[
        "patool",
        "colorama",
        "appdirs",
        "GitPython",
        "progressbar2>=3.2",
        'pywin32; platform_system == "Windows"',
        "RestrictedPython>=4.0",
        "redbaron",
        'python-sat; platform_system != "Windows"',
        'python-sat>=0.1.5.dev12; platform_system == "Windows"',
        "requests",
        "chardet",
        'importlib_metadata; python_version < "3.8"',
        "packaging",
        "fasteners>=0.16",
    ],
    setup_requires=["setuptools_scm", 'wheel; platform_system == "Windows"'],
    use_scm_version={"write_to": "portmod/_version.py"},
    extras_require={
        "dev": ["black", "flake8", "pylint", "isort", "mypy"],
        "test": ["pytest", "pytest-cov", "setuptools_scm"],
        "benchmark": ["pytest-benchmark"],
        "bash": ["argcomplete"],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Games/Entertainment",
        "Topic :: System :: Software Distribution",
    ],
)
