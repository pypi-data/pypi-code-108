'''Copyright (c) 2022 Z.ai Inc. ALL RIGHTS RESERVED

Z.ai official client SDK.
'''

import pathlib
import setuptools

long_description = (pathlib.Path(__file__)
                      .parent
                      .joinpath("README.md")
                      .read_text())

setuptools.setup(
    name="zaiclient",
    version="0.1.0",
    description="Z.ai official client SDK.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zaikorea/zaiclient",
    author="Z.ai Inc.",
    author_email="tech@zaikorea.org",
    license="Apache 2.0",
    # PyPI package information.
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=['zaiclient'],
    include_package_data=True,
    install_requires=pathlib.Path("requirements.txt").read_text().splitlines(),
    keywords="zai client sdk api ml",
)
