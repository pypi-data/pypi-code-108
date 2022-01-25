from .map_node import MapNode
from torch import nn

class DummyIdentityMapNode(MapNode):
    """A Dummy map node with Identity/linear layers. Mostly for testing purposes. """
    def __init__(self, name: str, numDims: int):
        super().__init__(name, numDims)

    def getEncoder(self, outputNode):
        return nn.Linear(in_features=self.numDims, out_features=outputNode.numDims)
    
    def getDecoder(self, inputNode):
        return nn.Identity()

    def aggregate(self):
        pass

    def getNodeCriterion(self):
        return lambda y, t : None
    
    def getNodeMetrics(self):
        return {}
