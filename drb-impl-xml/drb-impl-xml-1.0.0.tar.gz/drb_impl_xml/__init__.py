from . import _version
from .xml_node import XmlNode
from .xml_node_factory import XmlNodeFactory, XmlBaseNode

__version__ = _version.get_versions()['version']
__all__ = ['XmlBaseNode', 'XmlNode', 'XmlNodeFactory']
