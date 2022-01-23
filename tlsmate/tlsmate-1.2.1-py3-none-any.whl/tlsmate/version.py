# -*- coding: utf-8 -*-
"""Module providing the version
"""
# import basic stuff
import sys

# import own stuff

# import other stuff


if sys.version_info >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError
else:
    from importlib_metadata import version, PackageNotFoundError
try:
    __version__ = version("tlsmate")
except PackageNotFoundError:
    # package is not installed
    __version__ = "Cannot determine the version"
