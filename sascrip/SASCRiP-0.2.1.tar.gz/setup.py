# This is the setup file for my python package: DM_test_python_package

# Import required modules
from setuptools import setup
from setuptools import find_namespace_packages

# Load the ReadMe file
with open(file="./SASCRiP/README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

# Use the setup function to give all necessary information about the package
setup(
# Define the library name, this is what is used along with `pip install`
name = "SASCRiP",

# Define the author of the repository
author = "Darisia Moonsamy",

# Author email
author_email='darisia@outlook.com',

# Define the verison of this library
# Read this as
#   - MAJOR VERSION 0
#   - MINOR VERSION 2
#   - MAINTENANCE VERSION 1
version = "0.2.1",

# Here is a small description of the library.
# This appears when someone searches for the library on https://pypi.org/search
description = "A python package with wrapper functions that use the widely used Seurat and BUStools to perform single-cell RNA sequencing data pre-processing and visualisation",

# I have a long description but that will just be my readme file
long_description = long_description,

# This will specify that the long description is MARKDOWN
long_description_content_type = "text/markdown",

# Here is the url where you can find the code
url = "https://github.com/Darisia/SASCRiP",

# These are the dependencies the library needs to run
install_requires = [
'Kb-python==0.24.1'
],

keywords = 'single-cell RNA sequencing, data pre-processing, wrapper functions',

# Here are the packages I want to build
packages = find_namespace_packages(
    include=['SASCRiP', 'SASCRiP.*']
),

# Need to include the R scripts - otherwise only python scripts will be included
package_data = {
'SASCRiP': ['cqc_srt.R', 'cut_t2g.sh', 'edit_fastq_function.sh', 'edit_seurat_matrix.sh', 'install_packages.R', 'normalise_seurat.R']
},

# Include package data
include_package_data = True,

# Here I can specify the python version necessary to run this library
python_requires = ">=3.7",

# Additonal classifiers that give some characteristics about the package
# For a complete list go to https://pypi.org/classifiers/.
classifiers = [
'License :: OSI Approved :: GNU Affero General Public License v3',
'Natural Language :: English',
'Operating System :: Unix',
'Programming Language :: Python',
'Programming Language :: Python :: 3',
'Programming Language :: R',
'Programming Language :: Unix Shell'
]
)
