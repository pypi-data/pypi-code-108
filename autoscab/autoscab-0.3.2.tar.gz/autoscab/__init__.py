import sys
if sys.version_info.minor<8:
    from importlib_metadata import version
else:
    from importlib.metadata import version

__version__ = version("autoscab")
