#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bankster", # Replace with your own username
    version="0.0.4",
    author="Maciej Grela",
    author_email="enki@fsck.pl",
    description="Access information from financial institutions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mgrela/bankster",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Topic :: Office/Business :: Financial"
    ],
    python_requires='>=3.7',
    install_requires=[
        'selenium', 'structlog', 'requests', 'mechanicalsoup', 'beautifulsoup4', 'xdg'
    ]
)
