"""Contains custom types for type hinting."""
import os
import pathlib
from typing import TypeVar


PathLike = TypeVar('PathLike', str, bytes, os.PathLike, pathlib.Path)
