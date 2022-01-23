from setuptools import setup, find_packages
import codecs
import os
import pathlib

VERSION = '0.0.1'
DESCRIPTION = 'Anime info retrieving library. Currently Under development.'
LONG_DESCRIPTION = "Anime info retrieving library. Currently Under development. For more information, please visit https://github.com/ReZeroE/anime-python."


# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Setting up
setup(
    name="anime-python",
    version=VERSION,
    author="Kevin L. (ReZeroK)",
    author_email="kevinliu@vt.edu",
    license_file = "LICENSE.txt",
    license="GPLv3",
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ReZeroE/anime-python",
    packages=find_packages(),
    install_requires=['requests', 'pytest'],
    keywords=['python', 'anime', 'anilist', 'manga', 'light novel', 'characters', 'alpha testing', 'Milim', 'ReZeroK'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)