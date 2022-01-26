"""
Setup for lookatme.contrib.grapheasy
"""

import pathlib
from setuptools import setup, find_namespace_packages

cwd = pathlib.Path(__file__).parent
readme = (cwd / "README.md").read_text()
required = (cwd / "requirements.txt").read_text().splitlines()

setup(
    name="lookatme.contrib.grapheasy",
    version="1.0.0",
    description="Plugin for lookatme providing support for graph-easy.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/codybuell/lookatme.contrib.grapheasy",
    author="Cody Buell",
    author_email="cody@codybuell.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Environment :: Plugins",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics :: Presentation",
        "Topic :: Software Development :: Documentation",
    ],
    python_requires=">=3.9",
    install_requires=required,
    packages=find_namespace_packages(include=["lookatme.*"]),
)
