import re
import os

from setuptools import setup


def get_version():
    filename = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "efemarai/__init__.py"
    )
    with open(filename, "r") as f:
        for line in f.read().splitlines():
            match = re.search("^__version__ = [\"'](?P<version>.*)[\"']$", line)
            if match:
                return match.group("version")

        raise RuntimeError("Unable to find version string.")


def get_requirements(filename=None):
    if filename is None:
        filename = "requirements.txt"

    with open(filename) as f:
        requirements = [
            line
            for line in f.read().splitlines()
            if not line.startswith("#") and len(line) > 0
        ]
    return requirements


setup(
    name="efemarai",
    description="A CLI and SDK for interacting with the Efemarai ML testing platform.",
    version=get_version(),
    author="Efemarai",
    author_email="support@efemarai.com",
    url="https://www.efemarai.com/",
    license="MIT license",
    packages=["efemarai"],
    entry_points={"console_scripts": ["efemarai = efemarai.cli:main"]},
    install_requires=get_requirements(),
    python_requires=">=3.6",
    zip_safe=False,
)
