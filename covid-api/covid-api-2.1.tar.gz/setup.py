from setuptools import setup
from setuptools import find_packages

version = "2.1"

# This call to setup() does all the work
setup(
    name="covid-api",
    version=version,
    description="Get info about any country using https://disease.sh api",
    url="https://github.com/v1s1t0r999/CovidTracker/tree/v2-uc",
    author="v1s1t0r999",
    author_email="aditya.funs.11@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    packages=find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
)