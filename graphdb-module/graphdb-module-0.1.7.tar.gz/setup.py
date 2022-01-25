import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="graphdb-module",
    version="0.1.7",
    description="Wrapper for graphdb module",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://mnc-repo.mncdigital.com/ai-team/vision_plus/graph_db_module",
    author="AI Teams",
    author_email="ferdina.kusumah@mncgroup.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    install_requires=["pydantic", "pandas", "gremlinpython"],
)
