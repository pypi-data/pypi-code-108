# type: ignore[attr-defined]
"""Awesome `rdf-linkchecker` is a Python cli/package created with https://github.com/TezRomacH/python-package-template"""

import sys

import rdf_linkchecker.checkers.requests_based

if sys.version_info >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
