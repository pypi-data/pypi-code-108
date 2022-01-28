from io import BufferedIOBase, BytesIO
from typing import Union

from drb import DrbNode
from drb.factory.factory import DrbFactory

from drb_impl_json.json_node import JsonBaseNode, JsonNode


class JsonNodeFactory(DrbFactory):
    """
    The JsonNodeFactory class allow us to build drb nodes according
     to the form of the json you want to read.
    After this class is created you can call the _create method
     with the drb node created from the
    path of the Json file you want to read
    """
    def _create(self, node: Union[DrbNode, str]) -> DrbNode:
        if isinstance(node, DrbNode):
            if node.has_impl(BufferedIOBase):
                return JsonBaseNode(node, node.get_impl(BufferedIOBase))
            else:
                return JsonBaseNode(node, node.get_impl(BytesIO))
        return JsonNode(node)
