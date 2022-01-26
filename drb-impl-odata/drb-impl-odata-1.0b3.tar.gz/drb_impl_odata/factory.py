from drb import DrbNode
from drb.factory import DrbFactory

from .odata_nodes import ODataServiceNode


class OdataCscFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        return ODataServiceNode(node.path.name)
