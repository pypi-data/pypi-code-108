from io import BufferedIOBase, BytesIO

from drb import DrbNode
from .xml_node import XmlBaseNode
from drb.factory.factory import DrbFactory


class XmlNodeFactory(DrbFactory):

    def _create(self, node: DrbNode) -> DrbNode:
        if node.has_impl(BufferedIOBase):
            return XmlBaseNode(node, node.get_impl(BufferedIOBase))
        else:
            return XmlBaseNode(node, node.get_impl(BytesIO))
