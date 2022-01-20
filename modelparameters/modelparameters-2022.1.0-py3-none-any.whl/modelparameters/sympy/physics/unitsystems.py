"""
Deprecated: use ``sympy.physics.units``
"""

# DEPRECATED: use `units`
from ..utilities.exceptions import SymPyDeprecationWarning

exec("from .units import *")

SymPyDeprecationWarning(
    feature ="sympy.physics.unitsystems",
    useinstead ="sympy.physics.units",
    deprecated_since_version ="1.1",
    issue=12856,
).warn()
