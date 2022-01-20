from pkg_resources import get_distribution

# Get the version from the installed distribution (as established in setup.py)
__version__ = get_distribution('ntsbuildtools').version
