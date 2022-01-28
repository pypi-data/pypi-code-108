#!/usr/bin/env python3

from __future__ import print_function

import sys
import diffoscope

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


if sys.version_info < (3, 7):
    print("diffoscope requires at least python 3.7", file=sys.stderr)
    sys.exit(1)


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        super().initialize_options()
        self.pytest_args = []

    def finalize_options(self):
        super().finalize_options()
        if self.pytest_args:
            self.pytest_args = [self.pytest_args]

    def run_tests(self):
        # Inline import, otherwise the eggs aren't loaded
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="diffoscope",
    version=diffoscope.VERSION,
    description="in-depth comparison of files, archives, and directories",
    long_description=open("README.rst", encoding="utf-8").read(),
    long_description_content_type="text/x-rst",
    author="Diffoscope developers",
    author_email="diffoscope@lists.reproducible-builds.org",
    license="GPL-3+",
    url="https://diffoscope.org/",
    packages=find_packages(exclude=["tests", "tests.*"]),
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
    entry_points={
        "console_scripts": ["diffoscope=diffoscope.main:main"],
    },
    install_requires=[
        "python-magic",
        "libarchive-c",
    ],
    extras_require={
        "distro_detection": ["distro"],
        "cmdline": ["argcomplete", "progressbar"],
        "comparators": [
            "androguard",
            "binwalk",
            "defusedxml",
            "guestfs",
            "jsondiff",
            "python-debian",
            "pypdf2",
            "pyxattr",
            "rpm-python",
            "tlsh",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Utilities",
    ],
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#project-urls
    project_urls={
        "Issues": "https://salsa.debian.org/reproducible-builds/diffoscope/-/issues",
        "Merge requests": "https://salsa.debian.org/reproducible-builds/diffoscope/-/merge_requests",
    },
)
