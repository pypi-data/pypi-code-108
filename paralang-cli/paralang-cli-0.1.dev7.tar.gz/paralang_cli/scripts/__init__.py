"""
The scripts module containing the Para CLIs, where each file represents
a CLI. These include the Para Compiler CLI and tool CLIs
"""
from . import para
from . import paraproj

__all__ = [
    "para",
    "paraproj"
]