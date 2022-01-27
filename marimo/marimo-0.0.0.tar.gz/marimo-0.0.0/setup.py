from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="marimo",
    version="0.0.0",
    description="Marimo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
