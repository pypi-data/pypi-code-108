from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'eliot programming language'

# Setting up
setup(
    name="Elscript",
    version=VERSION,
    author="Kabuye Rogers",
    author_email="<eliotscript1@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['colorama'],
    keywords=['Runtime', 'Console', 'Interpreter'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)

