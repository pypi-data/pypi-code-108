"""setup.py"""
from setuptools import setup
from taoist import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="taoist",
    version=__version__,
    author="Daniel Garrigan",
    author_email="popgendad@gmail.com",
    description="Command line interface for Todoist",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/popgendad/taoist",
    packages=["taoist"],
    install_requires=[
        "tabulate>=0.8.9",
        "todoist_api_python>=1.1.0"
    ],
    python_requires=">=3.6",
    zip_safe=False,
    entry_points={"console_scripts": ["taoist=taoist.taoist_main:main"]},
)
