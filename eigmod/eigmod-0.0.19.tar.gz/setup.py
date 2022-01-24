from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.19'
DESCRIPTION = ''

# Setting up
setup(
    name="eigmod",
    version=VERSION,
    author="felix-95",
    author_email="felix.schaefer6@gmx.de",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pygame"],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3"
    ]
)
