
import pathlib

import setuptools

long_description = pathlib.Path("README.md").read_text()

setuptools.setup(
    name="dot4dict",
    version="0.1.0",
    author="zincwarecode",
    author_email="zincwarecode@gmail.com",
    description="A Python Package to enable dot-notation on dictionaries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zincware/dot4dict",
    download_url="https://github.com/zincware/dot4dict/archive/beta.tar.gz",
    keywords=["dotdict", "dict2dot"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)