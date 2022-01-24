"""
====================================
DRAMA Documentation (:mod:`drama`)
====================================

.. currentmodule:: DRAMA

DRAMA: **D**\elft **RA**\dar **M**\odeling and **P**\erformance **A**\ nalysis
"""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("drama").version
except Exception:
    # Local copy or not installed with setuptools.
    # Disable minimum version checks on downstream libraries.
    # Exception handling taken from xarray
    __version__ = "999"
