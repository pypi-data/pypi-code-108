from importlib_metadata import version
import setuptools
from pathlib import Path

setuptools.setup(
    name="mueidpdf",
    version=2,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests", "data"])
)
 