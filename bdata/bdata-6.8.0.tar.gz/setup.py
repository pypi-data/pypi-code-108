import setuptools
from distutils.core import Extension
import os

with open("README.md", "r", encoding = "utf8") as fh:
    long_description = fh.read()

# get setup variables
variables = {}
with open(os.path.join('bdata', 'version.py')) as fid:
    exec(fid.read(), variables)
    
__version__ = variables['__version__']

# setup
setuptools.setup(
    name = "bdata",
    version = __version__,
    author = "Derek Fujimoto",
    author_email = "fujimoto@phas.ubc.ca",
    description = "β-NMR/β-NQR MUD file reader and asymmetry calculator",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/dfujim/bdata",
    packages = setuptools.find_packages(),
    classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Development Status :: 5 - Production/Stable",
    ],
    install_requires = ['numpy >= 1.14', 'mud-py >= 1.2.8', 'scipy>=1.2.0',
                        'requests >= 2.22.0', 'pandas >= 0.25', 
                        'iminuit >= 2.6.1'],
)

