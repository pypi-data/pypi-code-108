# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Synapse Magic package."""

from .remotesynapsemagics import RemoteSynapseMagics, load_ipython_extension

__all__ = [
    'RemoteSynapseMagics',
    'load_ipython_extension'
]
