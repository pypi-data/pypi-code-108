from setuptools import setup, Extension, find_packages
import re

def find_version(fname):
    with open(fname,'r') as file:
        version_file=file.read()
        version_match = re.search(r"__VERSION__ = ['\"]([^'\"]*)['\"]",version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

with open("README.md", "r") as handle:
    cytolysis_description = handle.read()

version=find_version("src/cytosim_analysis.py")

setup(
    name='cytolysis',
    version=version,
    include_package_data=True,
    author="Serge Dmitrieff",
    description="An API to analyze cytosim simulations",
    long_description=cytolysis_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/SergeDmi/cytosim_analysis",
    install_requires=[
      'numpy',
      'pandas'
    ],
    packages=['cytolysis','cytolysis.example_data'],
    package_dir={'cytolysis': 'src', 'cytolysis.example_data': 'example_data'},
    package_data={'cytolysis': ['../*.md','*.md'], 'cytolysis.example_data': ['*.txt', '*.cym']},
 )
