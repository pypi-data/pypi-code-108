from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = '5.0.1'
DESCRIPTION = 'Library that simplifies using selenium'
LONG_DESCRIPTION = ''

# Setting up
setup(
    name="SeleniumKrystian",
    version=VERSION,
    author="Krystian Pielat",
    author_email="krystian.pielat@onet.pl",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['selenium', 'bs4'],
    keywords=['selenium', 'web scraping'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
