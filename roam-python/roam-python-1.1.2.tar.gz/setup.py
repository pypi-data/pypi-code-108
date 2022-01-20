import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="roam-python",
    version="1.1.2",
    description="Roam python SDK to listen to location updates.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="roam.ai",
    author_email="services@roam.ai",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(exclude=("tests",)),
    include_package_data=True,
    python_requires=">=3.5",
    # install_requires=["paho-mqtt-modified"]
    
    # For prod
    install_requires=["paho-mqtt"]
)