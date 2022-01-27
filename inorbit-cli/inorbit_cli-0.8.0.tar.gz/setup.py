# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

# TODO: filter files included on package dist (it currently includes tests folder)
# .local/bin/inorbit
# .local/lib/python3.8/site-packages/inorbit/*
# .local/lib/python3.8/site-packages/inorbit_cli-0.2.0.dist-info/*
# .local/lib/python3.8/site-packages/tests/*

setup(
    name="inorbit_cli",
    version="0.8.0",
    author="InOrbit Inc.",
    author_email="support@inorbit.ai",
    license="Proprietary",
    description="CLI tool to interact with InOrbit Cloud Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url = '<github url where the tool code will remain>',
    py_modules=[],
    packages=find_packages(),
    install_requires=[requirements],
    extras_require={
        "dev": [
            "twine",
            "lark",
            "pytest",
            "pytest-env",
            "requests-mock",
            "black",
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "License :: Other/Proprietary License",
    ],
    # see https://click.palletsprojects.com/en/8.0.x/setuptools/#setuptools-integration
    entry_points="""
        [console_scripts]
        inorbit = inorbit.cli:cli
    """,
)
