from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'ravspeak'
LONG_DESCRIPTION = 'A package to Speak '

# Setting up
setup(
    name="ravspeak",
    version=VERSION,
    author="Ravneet",
    author_email="weak47wale@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pyttsx3'],
    keywords=['speak','voice', 'jarvis' , 'audio'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)