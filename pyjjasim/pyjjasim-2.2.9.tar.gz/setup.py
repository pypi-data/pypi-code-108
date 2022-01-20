from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "pyjjasim/README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '2.2.9'
DESCRIPTION = 'Circuit simulator for josephson junctions and passive components'
LONG_DESCRIPTION = 'A package that allows simulating transport properties of arrays of josephson junctions.' \
                   'Features include time evolution and finding static configurations, external magnetic fields and' \
                   'thermal fluctuations.'

# Setting up
setup(
    name="pyjjasim",
    version=VERSION,
    author="Martijn Lankhorst",
    author_email="<m.lankhorst89@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy', 'scipy', 'matplotlib'],
    keywords=['python', 'josephson_junction_array', 'circuit', 'simulation'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)