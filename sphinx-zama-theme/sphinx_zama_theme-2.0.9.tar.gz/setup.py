"""Sphinx Bootstrap Theme package."""
import codecs
import os
import re

from setuptools import setup


# from https://packaging.python.org/guides/single-sourcing-package-version/
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(HERE, *parts), "r") as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Get the long description from the README file
with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

install_requires = []
requirementPath = os.path.join(HERE, "requirements.txt")
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(
    name="sphinx_zama_theme",
    version=find_version("sphinx_zama_theme", "__init__.py"),
    description="Zama sphinx theme forked from PyData sphinx theme",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zama-ai/sphinx_zama_theme",
    license="BSD",
    maintainer="Zama",
    maintainer_email="hello@zama.ai",
    packages=["sphinx_zama_theme"],
    include_package_data=True,
    # See http://www.sphinx-doc.org/en/stable/theming.html#distribute-your-theme-as-a-python-package
    entry_points={"sphinx.html_themes": ["sphinx_zama_theme = sphinx_zama_theme"]},
    install_requires=install_requires,
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Framework :: Sphinx",
        "Framework :: Sphinx :: Theme",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
