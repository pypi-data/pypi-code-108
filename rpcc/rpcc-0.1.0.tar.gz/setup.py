import pathlib
from setuptools import setup, find_packages
from rpcc.version import __version__

# package metadata
NAME = "rpcc"
DESCRIPTION = "A compiler for Mercury-based RPCs"
URL = "https://storage.bsc.es/projects/rpcc"
AUTHOR = "Alberto Miranda"
EMAIL = "alberto.miranda@bsc.es"

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name=NAME,
    version=__version__,
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=EMAIL,
    license="GPLv3",
    python_requires='>=3.6.0',
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Code Generators"
    ],
    entry_points={
        "console_scripts": [
            "rpcc = rpcc.__main__:main"
        ]
    },
)
