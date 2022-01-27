"""Setup script for coinlib"""
import os.path
from setuptools import setup
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README_pip.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="pipedash",
    version="1.2.8",
    description="Develop new code for your pipedash widgets",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/pipedash/pipedash-python",
    author="pipedash",
    author_email="donnercody86@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(include=('pipedash*',)),
    include_package_data=True,
    install_requires=[
        "requests", "semver", "datascience", "munch", "coolname", "google", "pika", "aio_pika", "grpcio", "grpcio-tools", "protobuf", "cython", "ipython", "ipykernel", "pandas", "websocket-client", "plotly", "simplejson", "ipynb_path",
        "pyarrow", "pandas", "python-dateutil"
    ],
    entry_points={"console_scripts": ["pipedash=index:main"]},
)
