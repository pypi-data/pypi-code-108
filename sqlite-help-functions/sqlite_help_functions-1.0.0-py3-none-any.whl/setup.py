import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sqlite_help_functions",
    version="1.0.0",
    description="Sql helper: No need to worry about syntax when doing sqlite3 in python3",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/TvoozMagnificent/sql",
    author="TvoozMagnificent",
    author_email="luchang1106@icloud.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["sqlite_help_functions"],
    include_package_data=True,
    install_requires=[],
)


