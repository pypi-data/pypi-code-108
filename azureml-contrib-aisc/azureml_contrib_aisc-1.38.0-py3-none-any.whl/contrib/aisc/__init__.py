# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This package include compute sub package."""
from . import _hooks

from azureml._base_sdk_common import __version__ as VERSION
from .aisc_run import AISCRun

__version__ = VERSION

__all__ = [
    'AISCRun'
]
