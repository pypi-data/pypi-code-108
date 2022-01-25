#! /usr/bin/env python3

import setuptools

from PyOBEX import __version__

DESCRIPTION = ("A package implementing aspects "
               "of the Object Exchange (OBEX) protocol.")

setuptools.setup(
    name="PyOBEX",
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author="David Boddie",
    author_email="david@boddie.org.uk",
    url="https://gitlab.com/dboddie/pyobex",
    version=__version__,
    license="GPL version 3 (or later)",
    platforms="Cross-platform",
    packages=["PyOBEX"],
    install_requires=["PyBluez >= 0.23"],
    project_urls={
        "Bug Reports": "https://gitlab.com/dboddie/pyobex/-/issues",
        "Source": "https://gitlab.com/dboddie/pyobex",
    }
)
