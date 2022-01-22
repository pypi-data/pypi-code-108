__version__ = '0.0.2-alpha'

# thanks tensorflow open source :D
# Special dunders that we choose to export:
_exported_dunders = set([
    '__version__',
    '__git_version__'
])

# This is necessary to export our dunders.
__all__ = [s for s in dir() if s in _exported_dunders or not s.startswith('_')]