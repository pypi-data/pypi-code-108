import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname), "r").read()

def get_version():
    g = {}
    exec(open(os.path.join("stompy", "version.py"), "r").read(), g)
    return g["Version"]


setup(
    name = "stompymq",
    version = get_version(),
    author = "Igor Mandrichenko",
    author_email = "igorvm@gmail.com",
    description = ("Python implementation of STOMP protocol and message broker"),
    license = "BSD 3-clause",
    keywords = "STOMP, message queue, message broker",
    url = "https://github.com/imandr/stompymq",
    packages=['stompy'],
    long_description=read('README.md'),
    install_requires=["pythreader >= 1.7"],
    zip_safe = False,
    classifiers=[
    ],
    entry_points = {
            #"console_scripts": [
            #    "metacat = metacat.ui.metacat_ui:main",
            #]
        }
)