import codeop
from ctypes.wintypes import LONG
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.3"
DESCRIPTION = "Labguru API python support"
LONG_DESCRIPTION = "Python wrapper for the Labguru RESTful API"

# Setting up
setup(
    name = "pyguru",
    version = VERSION,
    author = "jteske54",
    author_email="teske.jacob@gmail.com",
    url="https://github.com/jteske54/pyguru",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests','pandas','numpy'],
    keywords=['python','labguru','pyguru','lab','guru'],



)