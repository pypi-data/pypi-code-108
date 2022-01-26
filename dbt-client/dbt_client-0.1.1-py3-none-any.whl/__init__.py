"""
A simple client for DBT RPC instances
"""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

from dbt_client.dbt_client import DbtClient

__version__ = importlib_metadata.version(__name__)

__all__ = [
    '__version__',
    "DbtClient",
]
