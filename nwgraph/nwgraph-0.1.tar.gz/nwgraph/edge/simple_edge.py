import torch.nn as nn
from overrides import overrides
from typing import Callable
from nwutils.nwmodule import trModuleWrapper
from nwmodule import NWModule

from .edge import Edge
from ..logger import logger

class SimpleEdge(Edge):
	@overrides
	def getModel(self) -> NWModule:
		if hasattr(self, "model"):
			logger.info("Model already instantiated, returning early.")
			return self.model
		A, B = self.inputNode, self.outputNode
		encoder = A.getEncoder(B)
		decoder = B.getDecoder(A)
		model = trModuleWrapper(nn.Sequential(encoder, decoder))
		self.addMetrics(B.getNodeMetrics())
		return model

	@overrides
	def getCriterion(self) -> Callable:
		return self.outputNode.getNodeCriterion()
