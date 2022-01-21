from nwgraph import Node

class MapNode(Node):
    """Generic Map Node (2D) having a number of channels (D1xD2xNC)"""
    def __init__(self, name: str, numDims: int, hyperParameters: dict={}):
        Node.__init__(self, name, hyperParameters)
        self.numDims = numDims
