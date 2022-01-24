from pathlib import Path
from packaging.version import parse

with Path(__file__).with_name('_version.txt').open('r') as f:
    __version__ = parse(f.readline().strip())

# Representation of version_info as (x, y, z)
version_info = __version__.release

__all__ = ('__version__', 'version_info')
