# type: ignore
try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

__version__: str = version(__name__)
