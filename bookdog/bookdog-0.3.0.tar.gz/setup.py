"""Setup script for realpython-reader"""

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
NAME = "bookdog"

# This call to setup() does all the work
setup(
    name=NAME,
    version="0.3.0",
    description="Track books you've read or listened to",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/jima80525/bookdog",
    author="Jim Anderson",
    author_email="jima.coding@gmail.com",
    python_requires=">=3.8.0",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=[NAME],
    include_package_data=False,
    install_requires=[
        "PySimpleGUI==4.55.1",
    ],
    entry_points={"console_scripts": ["bookdog=bookdog.__main__:main"]},
)
