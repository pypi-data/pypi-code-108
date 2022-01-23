"""
Functionality related to the Q-CTRL graph structure.

The commons objects are re-imported here to allow all access to the objects to happen directly from
the `qctrl` package.
"""

import sys

# We import Graph to expose it directly from this module.
# pylint: disable=unused-import
from qctrlcommons.graph import Graph
from qctrlcommons.node.registry import TYPE_REGISTRY as _TYPE_REGISTRY

_module = sys.modules[__name__]
for _type_cls in _TYPE_REGISTRY:
    setattr(_module, _type_cls.__name__, _type_cls)
