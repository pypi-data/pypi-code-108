"""
common dataclasses
"""

from dataclasses import dataclass


@dataclass
class Error:
    """
    SearchV1Error
    """
    error: str
