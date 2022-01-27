import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ystreamer",
    version="1.1.0",
    description="API to interact with Yahoo Finance Websocket API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/bwees/ystreamer",
    author="bwees",
    author_email="brandonwees@gmail.com",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["ystreamer"],
    include_package_data=True,
    install_requires=["websocket-client", "protobuf"]
)
