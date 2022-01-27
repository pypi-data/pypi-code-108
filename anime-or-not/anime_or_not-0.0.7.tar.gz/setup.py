from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.7'
DESCRIPTION = 'Classifies if an image is "anime" or not'
LONG_DESCRIPTION = 'Classifies if an image is "anime" or not'

# Setting up
setup(
    name="anime_or_not",
    version=VERSION,
    author="LaihoE",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['onnxruntime', 'Pillow', 'torchvision','torch'],
    include_package_data=True
)

