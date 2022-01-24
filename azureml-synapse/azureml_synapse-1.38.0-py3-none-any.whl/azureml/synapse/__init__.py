# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Synapse package."""

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

try:
    from ._version import ver
    __version__ = ver
except ImportError:
    __version__ = '0.0.0+dev'
