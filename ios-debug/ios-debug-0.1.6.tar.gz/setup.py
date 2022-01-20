import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ios-debug",
    version="0.1.6",
    description="Debug mode manager for iOS.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="Tom Novotny",
    author_email="tom.novota@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(include=["iosdebug", "iosdebug.*"]),
    include_package_data=True,
    install_requires=["prompt-toolkit", "psutil", "gitpython"],
    entry_points={
        "console_scripts": [
            "ios-debug=iosdebug.__main__:main",
        ]
    },
)
