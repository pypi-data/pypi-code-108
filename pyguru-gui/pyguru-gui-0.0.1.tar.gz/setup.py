import codeop
from ctypes.wintypes import LONG
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.1"
DESCRIPTION = "GUI Labguru API python support"
LONG_DESCRIPTION = "Python GUI for the Labguru RESTful API"

# Setting up
setup(
    name = "pyguru-gui",
    version = VERSION,
    author = "jteske54",
    author_email="teske.jacob@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pyguru'],
    keywords=['python','labguru','pyguru','lab','guru','gui'],
    


)