"""
Installer for ExoSense Client
"""
import os
from setuptools import setup, find_packages
import __version__

DOCS_URL = 'https://github.com/TheGravityMan/Prism-Quest'

INSTALL_REQUIRES = [
    'random'
]


def read(fname):
    """ Primarily used to open README file. """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


try:
    README = read('README.rst')
except:
    README = ''

setup(
    name="PrismQuest",
    version="1.0.5",
    author="The Gravity Man",
    author_email="patrickjshanks@gmail.com.com",
    description="""Prism Quest is a text-based game.""",
    license="Apache 2.0",
    keywords="prism quest",
    url="https://github.com/TheGravityMan/Prism-Quest",
    packages=find_packages(),
    entry_points={
        'console_scripts': []
    },
    install_requires=INSTALL_REQUIRES,
    long_description=README,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Internet",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Telecommunications Industry",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
    ],
    )
