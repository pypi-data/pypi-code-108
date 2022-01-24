"""Setup script for realpython-reader"""

import os.path
from setuptools import setup, find_packages

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(name="onnc-bench",
      version="2.4.0",
      description="ONNC-bench is a Python wrapper of ONNC",
      long_description=README,
      long_description_content_type="text/markdown",
      url="https://www.skymizer.com",
      author="The Skymizer Team",
      author_email="hello@skymizer.com",
      license="Apache License 2.0",
      packages=find_packages(),
      package_data={"onnc": ["*"]},
      data_files=[],
      install_requires=["requests", "numpy", "onnx", "loguru", "sentry-sdk"])
