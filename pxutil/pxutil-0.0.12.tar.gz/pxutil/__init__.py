"""
pxutil
~~~~~

Peter Jiping Xie's personal utils.

:copyright: © 2019 by Peter Jiping Xie.
:license: MIT.
"""

# Control the version directly in setup.py
# __version__ = '0.0.1'

# import func/classes from .pxutil here so users can them directly, i.e. pxutil.bash() instead of pxutl.pxutil.bash().
from .pxutil import bash, bashx, trim_docstring, grep, purge, time2seconds, replace_in_file
