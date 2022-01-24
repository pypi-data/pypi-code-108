# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Init for standard AutoML modules. This package is imported directly by AutoML
components in the Jasmine repo.
"""

__all__ = []

try:
    from ._version import ver
    __version__ = ver
except ImportError:
    __version__ = '0.0.0+dev'
