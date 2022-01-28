from . import _version
from .odata_nodes import ODataServiceNode, ODataProductNode, ODataAttributeNode
from .odata_utils import ODataQueryPredicate

__version__ = _version.get_versions()['version']
__all__ = [
    'ODataServiceNode',
    'ODataProductNode',
    'ODataAttributeNode',
    'ODataQueryPredicate'
]
