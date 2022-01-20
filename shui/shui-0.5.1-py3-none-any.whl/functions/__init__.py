"""Module for functions that interact with the remote Apache server"""
from .file_details import get_file_details
from .install import extract_tarball
from .versions import get_versions

__all__ = [
    "extract_tarball",
    "get_file_details",
    "get_versions",
]
