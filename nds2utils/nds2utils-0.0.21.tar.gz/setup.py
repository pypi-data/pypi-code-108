import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

from distutils.util import convert_path
main_ns = {}
ver_path = convert_path('nds2utils/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

setuptools.setup(
    name="nds2utils",
    version=main_ns['__version__'],
    author="Craig Cahillane",
    author_email="ccahilla@caltech.edu",
    description="nds2 utilities for reading LIGO data quickly and easily",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.ligo.org/craig-cahillane/nds2utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
