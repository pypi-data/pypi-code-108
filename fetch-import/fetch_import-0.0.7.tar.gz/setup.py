from setuptools import find_packages
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = '0.0.7'

setup(
    name='fetch_import',
    version=VERSION,
    author="zmaplex",
    author_email="zmaplex@gmail.com",
    description="Import Python packages from remote.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zmaplex/fetch_import",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.6",
)
