"""Top-level package for j-chess-lib."""
from .communication import schema_version

__author__ = """RedRem95"""
__version__ = '0.2.4'
__schema_version__ = schema_version

print(f"Loading j-chess-lib v-{__version__} by {__author__}. Using schema-version v-{schema_version}")
