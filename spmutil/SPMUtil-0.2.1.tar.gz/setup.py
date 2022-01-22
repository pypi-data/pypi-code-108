import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding="utf-8") as f:
    description = f.read()

setuptools.setup(
    name="SPMUtil",
    version="0.2.1",
    description="Some Common method for SPM data analysis and realtime data processing.",
    author="ZHUO DIAO",
    author_email="enzian0515@gmail.com",
    license="LGPL",
    packages=setuptools.find_packages(),
    long_description=description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=["scipy", "matplotlib", "pandas", "nanonispy"]
)