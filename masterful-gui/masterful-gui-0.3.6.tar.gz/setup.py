"""Pip package configuration module."""

import os
from setuptools import setup, find_packages

import masterful_gui.version as version

with open("README.md", "r") as f:
  _LONG_DESCRIPTION = f.read()


def get_required_packages():
  file_path = f"{os.getcwd()}/requirements.txt"
  with open(file_path) as f:
    return f.read().splitlines()


REQUIRED_PACKAGES = get_required_packages()

# The script that defines the command to run the GUI.
CONSOLE_SCRIPTS = [
    "masterful-gui = masterful_gui.main:run_main",
]

setup(
    name='masterful-gui',
    version=version.__version__,
    author="Masterful AI",
    author_email="help@masterfulai.com",
    description="Masterful AutoML Platform GUI.",
    long_description=_LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://masterfulai.com",
    license='Copyright 2022, Masterful AI, Inc.',
    license_files=('LICENSE',),
    packages=find_packages(),
    entry_points={
        "console_scripts": CONSOLE_SCRIPTS,
    },
    install_requires=REQUIRED_PACKAGES,
    include_package_data=True,
    python_requires=">=3.6",
)
