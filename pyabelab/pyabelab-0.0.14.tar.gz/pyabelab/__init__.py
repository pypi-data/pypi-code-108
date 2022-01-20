"""Library that are likely to be used frequently in ABELAB.
"""

try:
    from .version import __version__  # NOQA
except ImportError:
    raise ImportError("BUG: version.py doesn't exist. Please file a bug report.")
