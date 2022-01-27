from io import open
from setuptools import setup, find_packages


def read(f):
    return open(f, "r").read()


setup(
    name="mongodantic",
    version='0.2.2b1',
    packages=find_packages(exclude=("tests", "docs", "examples")),
    install_requires=[
        "pydantic>=1.3,<2",
        "pymongo>=3.10.1",
    ],
    description="Mongo ODM, based on pydantic and pymongo",
    author="bzdvdn",
    author_email="bzdv.dn@gmail.com",
    url="https://github.com/bzdvdn/mongodantic",
    license="MIT",
    python_requires=">=3.7",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
)
