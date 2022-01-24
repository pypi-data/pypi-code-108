import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="nso_restconf",
    version="1.0.0",
    description="A wrapper for managing the API of NSO",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rtrjl/nso_restconf",
    author="Rodolphe Trujillo",
    author_email="rodtruji@cisco.com",
    license="Cisco Sample Code License, Version 1.1",
    classifiers=[
        "Topic :: System :: Networking",
    ],
    packages=["nso_restconf"],
    include_package_data=True,
    install_requires=["requests"],
    requires_python='>=3.7.0'

)
