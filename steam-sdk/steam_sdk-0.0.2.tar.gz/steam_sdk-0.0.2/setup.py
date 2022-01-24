from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='steam_sdk',
    version="0.0.2",
    author="Mariusz Wozniak",
    author_email="mariusz.wozniak@cern.ch",
    description="Source code for APIs for STEAM tools.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.cern.ch/steam/steam_sdk",
    keywords={'STEAM', 'API', 'CERN'},
    install_requires=["numpy"],
    extras_require={"dev": ["pandas", "matplotlib",],},
    python_requires='>=3.8',
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8"],

)
