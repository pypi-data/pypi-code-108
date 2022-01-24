import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="nso_live_status",
    version="1.0.2",
    description="Retrieve cli result and parse it using NSO live status and PyATS parsers",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rtrjl/nso_live_status",
    author="Rodolphe Trujillo",
    author_email="rodtruji@cisco.com",
    license="Cisco Sample Code License, Version 1.1",
    classifiers=[
        "Topic :: System :: Networking",
    ],
    packages=["nso_live_status"],
    include_package_data=True,
    install_requires=["pyats_parser"],
    requires_python='>=3.6.0'

)
