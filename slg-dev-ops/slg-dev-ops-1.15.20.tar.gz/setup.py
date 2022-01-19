"""Module setup."""

import runpy
from setuptools import setup, find_packages
from slg_setup import get_script_files

PACKAGE_NAME = "slg-dev-ops"
version_meta = runpy.run_path("./version.py")
VERSION = version_meta["__version__"]


with open("README.md", "r") as fh:
    long_description = fh.read()


def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


if __name__ == "__main__":
    setup(
        name=PACKAGE_NAME,
        version=VERSION,
        packages=find_packages(),
        install_requires=parse_requirements("requirements.txt"),
        python_requires=">=3.6.3",
        scripts=get_script_files(),
        description="This is a description.",
        long_description=long_description,
        long_description_content_type="text/markdown",
    )
