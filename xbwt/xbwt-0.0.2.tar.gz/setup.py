from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.2'
DESCRIPTION = 'Construction of the xbw transform'
LONG_DESCRIPTION = 'An implementation of the PathSort algorithm defined in [Ferragina, Paolo et al. "Compression and Indexing of Labeled Trees, with Applications". J. ACM 57 (2009): 4: 1-4: 33.] for the construction of the xbw transform.'

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