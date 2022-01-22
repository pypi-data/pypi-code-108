from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

packages = find_packages()

setup_args = {
    "name": "robotframework-dateextension",
    "version": "0.1.0",
    "description": "Extension of robotframework's DateTime library. This library allows for assertions related to dates and times.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "Robin Matz",
    "author_email": "robin.s.matz@gmail.com",
    "url": "https://github.com/robinmatz/robotframework-dateextension",
    "packages": packages,
    "install_requires": ["robotframework"]
}

setup(**setup_args)
