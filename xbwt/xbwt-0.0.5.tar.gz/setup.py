from setuptools import setup, find_packages
import codecs
import os
# read the contents of your README file
from pathlib import Path

VERSION = '0.0.5'
DESCRIPTION = 'Construction of the xbw transform'

this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

# Setting up
setup(
    name="xbwt",
    version=VERSION,
    author="NeuralNine (Florian Dedov)",
    author_email="<dolcedanilo1995@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    url="https://github.com/dolce95/xbw-transform",
    install_requires=['numpy'],
    keywords=['python', 'xbwt', 'compression and indexing of labeled trees'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)