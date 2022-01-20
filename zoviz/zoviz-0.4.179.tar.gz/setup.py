import os
from setuptools import setup, find_packages

metadata = {}
with open("zoviz/metadata.py") as f:
    exec(f.read(), metadata)  # Collect metadata

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='zoviz',
    version=metadata["__version__"],
    description=metadata["__description__"],
    author=metadata["__author__"],
    author_email=metadata["__author_email__"],
    url=metadata["__url__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["ci", "tests"]),
    install_requires=[
        "matplotlib",
        "networkx",
        "seaborn",
        "pandas",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
