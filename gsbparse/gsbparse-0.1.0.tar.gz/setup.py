"""Defines package and entry points of met2db package."""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gsbparse",
    version="0.1.0",
    url="https://github.com/EBoisseauSierra/gsbparse",
    description="A simple parser for your Grisbi's .gsb account files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Étienne Boisseau-Sierra",
    author_email="etienne.boisseau.sierra@gmail.com",
    maintainer="Étienne Boisseau-Sierra",
    maintainer_email="etienne.boisseau.sierra@gmail.com",
    packages=setuptools.find_packages(),
    install_requires=["defusedxml", "pandas"],
    extras_require={
        "dev": ["black", "flake8", "pre-commit", "pylint"],
        "test": ["pytest", "pytest-cov"],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    license="MIT",
    python_requires=">=3.9",
)
