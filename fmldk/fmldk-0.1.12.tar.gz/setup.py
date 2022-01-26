
from pathlib import Path
from setuptools import setup

# The directory containing this file
this_directory = Path(__file__).parent
long_description  = (this_directory / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="fmldk",
    version="0.1.12",
    description="Forecast ML library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rahul Sinha",
    author_email="rahul.sinha@unilever.com",
    packages=["tfr"],
    include_package_data=True,
    install_requires=["tensorflow", "tensorflow_probability", "numpy", "pandas", "joblib", "pathlib"]
)