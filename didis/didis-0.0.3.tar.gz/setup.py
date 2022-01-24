import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
print(long_description)
# This call to setup() does all the work
setup(
    name="didis",
    version="0.0.3",
    description="DIDIS - Desy ITk Database Interaction Script",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://gitlab.cern.ch/mcaspar/didis",
    author="Maximilian Caspar",
    author_email="maximilian.caspar@desy.de",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["didis"],
    include_package_data=True,
    install_requires=["loguru", "argh", "itkdb", "pyyaml", "openpyxl"],
    entry_points={
        "console_scripts": [
            "didis=didis.didis:main",
            "didis-batch=didis.batch:main"
        ]
    },
)
