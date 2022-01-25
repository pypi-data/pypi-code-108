from nwgraph import Node

# @brief Generic Vector Node (1D) having a number of channels (DxNC)
class VectorNode(Node):
	def __init__(self, name: str, numDims: int, hyperParameters: dict={}):
		super().__init__(name, hyperParameters)
		self.numDims = numDims
