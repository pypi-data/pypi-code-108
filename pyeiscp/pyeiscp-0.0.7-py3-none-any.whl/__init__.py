"""Onkyo receiver Interface Module.

This module provides a unified asyncio network handler for interacting with
home A/V receivers and processors made by Onkyo.
"""
from pyeiscp.connection import Connection  # noqa: F401
from pyeiscp.protocol import AVR  # noqa: F401
import pyeiscp.tools
