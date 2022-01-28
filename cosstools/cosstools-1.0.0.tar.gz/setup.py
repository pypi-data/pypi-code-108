from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.0'
DESCRIPTION = 'Python tools by Alessandro Cossard for the CRYSTAL software'

# Setting up
setup(
    name="cosstools",
    version=VERSION,
    author="Alessandro Cossard",
    author_email="<alessandro.cossard@unito.it>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'chemistry', 'physics', 'crystal', 'topond', 'quantum'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
