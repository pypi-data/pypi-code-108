import os
import re

from setuptools import find_packages, setup  # type: ignore


def read_file(filename: str) -> str:
    """Read package file as text to get name and version."""
    cwd = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(cwd, "suno", filename)) as f:
        return f.read()


def find_version() -> str:
    """Only define version in one place."""
    text = read_file("__init__.py")
    m_version = re.search(r"^__version__ = [\"\']([^\"\']*)[\"\']$", text, re.M)
    if m_version:
        return m_version.group(1)
    raise RuntimeError("Could not find version string.")


def find_name() -> str:
    """Only define name in one place."""
    text = read_file("__init__.py")
    m_name = re.search(r"^__package_name__ = [\"\']([^\"\']*)[\"\']$", text, re.M)
    if m_name:
        return m_name.group(1)
    raise RuntimeError("Could not find name string.")


def find_long_description() -> str:
    """Return the content of the README.md file."""
    return read_file("../README.md")


setup(
    name=find_name(),
    version=find_version(),
    description="Suno audio tools.",
    long_description=find_long_description(),
    long_description_content_type="text/markdown",
    # url="https://github.com/suno-ai/suno",
    author="suno.ai",
    # author_email="code@suno.com",
    # license="Apache 2.0",
    packages=find_packages(),
    install_requires=[],
    extras_require={},
    package_data={},
    dependency_links=[],
)
