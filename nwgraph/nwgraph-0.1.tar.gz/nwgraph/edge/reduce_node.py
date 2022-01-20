from typing import Callable
from nwutils.nwmodule import trModuleWrapper
from .edge import Edge
from ..node import Node

class ReduceNode(Edge):
	def __init__(self, inputNode:Node, forwardFn:Callable, *args, **kwargs):
		super().__init__(inputNode, inputNode, *args, **kwargs)
		self.forwardFn = forwardFn
		self.inputNode = inputNode

	def forward(self, x):
		return self.forwardFn(x, self)

	def getDecoder(self):
		return trModuleWrapper(lambda x : x)

	def getEncoder(self):
		return trModuleWrapper(lambda x : x)

	def getCriterion(self):
		return self.inputNode.getNodeCriterion()

	def getModel(self):
		pass

	def __str__(self):
		return "ReduceNode %s" % (str(self.inputNode))

class ReduceEdge: pass
