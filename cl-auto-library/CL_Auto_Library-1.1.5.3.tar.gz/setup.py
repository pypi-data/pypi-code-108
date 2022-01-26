import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

# The execution of the Setup.py will install your package and all dependencies
# when you install the custom library using, pip install <custom_library_name> on the command line.
# It is not mandatory to create a requirements.txt file, you can just set the
# install_requires directly, but creating a requirements.txt file is best practice.	
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = ["openpyxl", "xlrd", "psutil", "python-docx"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
	
setuptools.setup(
    name="CL_Auto_Library", # A custom Library
    version="1.1.5.3",
    author="sieqqc",
    author_email="sieqqc@gmail.com",
    description="A custom Library",
    long_description="A custom Library",
    long_description_content_type="text/markdown",
	install_requires=["openpyxl", "xlrd", "psutil", "python-docx"],
    url="http://10.21.37.110/corp_sieq/Partner%20Automation%20Testing%20Trial/_git/CL_Auto_Library",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)