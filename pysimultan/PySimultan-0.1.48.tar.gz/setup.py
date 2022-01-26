from distutils.core import setup, Extension
from pathlib import Path

import setuptools

project_dir = Path(__file__).parent

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name="PySimultan",
    version="0.1.48",
    description="Python Package to import and work with the SIMULTAN Data model",
    # Allow UTF-8 characters in README with encoding argument.
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=["python"],
    author="Max Buehler",
    url="https://github.com/bph-tuwien/PySimultan",
    packages=["PySimultan"],
    package_dir={"PySimultan": "src/PySimultan"},
    package_data={'PySimultan': ['resources/*']},
    # pip 9.0+ will inspect this field when installing to help users install a
    # compatible version of the library for their Python version.
    python_requires=">=3.7",
    setup_requires=["wheel"],
    # There are some peculiarities on how to include package data for source
    # distributions using setuptools. You also need to add entries for package
    # data to MANIFEST.in.
    # See https://stackoverflow.com/questions/7522250/
    include_package_data=True,
    # This is a trick to avoid duplicating dependencies between both setup.py and
    # requirements.txt.
    # requirements.txt must be included in MANIFEST.in for this to work.
    # It does not work for all types of dependencies (e.g. VCS dependencies).
    # For VCS dependencies, use pip >= 19 and the PEP 508 syntax.
    #   Example: 'requests @ git+https://github.com/requests/requests.git@branch_or_tag'
    #   See: https://github.com/pypa/pip/issues/6162
    install_requires=project_dir.joinpath("requirements.txt").read_text().split("\n"),
    zip_safe=True,
    license="MIT",
    license_files=["LICENSE.txt"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    entry_points={"console_scripts": ["PySimultan=PySimultan.cli:main"]},
)
