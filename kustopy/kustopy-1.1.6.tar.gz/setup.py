import pathlib
from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="kustopy",
    version="1.1.6",
    description="Query and Ingestion Client for Azure using Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tillfurger/kustopy",
    author="Till Furger",
    author_email="till@furger.net",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["kustopy"],
    include_package_data=True,
    install_requires=["azure-kusto-data", "azure-kusto-ingest", "pandas"],
    entry_points={
        "console_scripts": [
            "tillfurger=kustopy.__main__:main",
        ]
    },
)