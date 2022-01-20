import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

import sys
sys.path.append(str(HERE / "src"))
print(sys.path)
from twitterstatsazure import VERSION

# The text of the README file
README = (HERE / "README.md").read_text()


# This call to setup() does all the work
setup(
    name="twitterstatsazure",
    version=VERSION,
    description="Python Package to collect stats from Twitter API and store them to Azure Blob Storage",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://bas.codes",
    author="Bas Steins",
    author_email="opensource@bas.codes",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["twitterstatsazure"],
    include_package_data=False,
    install_requires=[
        "setuptools>=42",
        "wheel",
        "azure-storage-blob>=12.9.0",
        "TwitterAPI>=2.7.11",
    ],
)
