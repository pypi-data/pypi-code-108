
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.5.5.8'
DESCRIPTION = 'Api Module for https://bubblez.app/ and websockets'

# Setting up
setup(
    name="Bubblez.py",
    version=VERSION,
    author="Mees Meijer (Discord: @MeeSOS#1721)  support@meesinc.nl",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    requires=['wheel'],
    packages=[
        "Bubblez", "examples", 
        "Bubblez.classes", "Bubblez.classes.api", "Bubblez.classes.api.send", "Bubblez.classes.api.receive", 
        "Bubblez.classes.socket", "Bubblez.classes.socket.receive","Bubblez.classes.socket.events",
        "Bubblez.socket"],
    install_requires=['requests'],
    keywords=['python', 'api', "websockets"],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
