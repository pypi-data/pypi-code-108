#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=7.0",
]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Taylor Monacelli",
    author_email="taylormonacelli@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={
        "console_scripts": [
            "mulltours=mulltours.cli:main",
        ],
    },
    install_requires=["cookiecutter", "clinepunk", "GitPython"],
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="mulltours",
    name="mulltours",
    packages=find_packages(include=["mulltours", "mulltours.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/TaylorMonacelli/mulltours",
    version="0.1.5",
    zip_safe=False,
)
