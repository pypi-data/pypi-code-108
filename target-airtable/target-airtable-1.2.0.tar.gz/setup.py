#!/usr/bin/env python
import sys
import os
from setuptools.command.install import install
from setuptools import setup, find_packages

VERSION = "v1.2.0"


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('TAG_NAME')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setup(
    name="target-airtable",
    version=VERSION,
    license="GNU Affero General Public License v3.0",
    description="Singer.io target for loading data",
    author="ednarb29",
    url="https://github.com/ednarb29/target-airtable",
    keywords=["singer.io", "singer-target", "airtable"],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Affero General Public License v3"
    ],
    py_modules=["target_airtable"],
    install_requires=[
        "singer-python>=5.0.12",
        "requests>=2.27.1"
    ],
    entry_points="""
    [console_scripts]
    target-airtable=target_airtable:main
    """,
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
