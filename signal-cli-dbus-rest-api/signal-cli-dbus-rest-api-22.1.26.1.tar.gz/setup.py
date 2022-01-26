"""
signal-cli-dbus-rest-api
"""

import codecs
import os.path
from pathlib import Path

from setuptools import find_packages, setup


def read(rel_path):
    """
    read
    """
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as f_p:
        return f_p.read()


def get_version(rel_path):
    """
    get_version
    """
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")


# read the contents of your README file
DIR = Path(__file__).parent
LONG_DESCRIPTION = (DIR / "README.md").read_text()

setup(
    name="signal-cli-dbus-rest-api",
    author="Stefan Heitmüller",
    author_email="stefan.heitmueller@gmx.com",
    license="MIT",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires="~=3.7",
    packages=find_packages(),
    version=get_version("signal_cli_dbus_rest_api/version/__init__.py"),
    install_requires=[
        "sanic==21.12.1",
        "sanic-ext==22.1.2",
        "python-magic==0.4.24",
        "pydbus==0.6.0",
    ],
    entry_points={
        "console_scripts": ["signal-cli-dbus-rest-api=signal_cli_dbus_rest_api:run"],
    },
)
