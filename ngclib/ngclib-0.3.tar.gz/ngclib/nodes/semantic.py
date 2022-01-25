from typing import Dict, List, Union, Tuple
from functools import partial
from overrides import overrides
from torchmetrics import Metric
from torchmetrics.functional import accuracy
from nwmodule.nwmodule import CriterionType
from nwmodule.loss import softmax_nll

from .map_node import MapNode

def dice_loss(y, t, nClasses: int, classWeights: List=None):
	if classWeights is None:
		classWeights = [1] * nClasses

	smooth = 1.
	loss = 0.
	for c in range(nClasses):
		iflat = y[..., c].view(-1)
		tflat = t[..., c].view(-1)
		intersection = (iflat * tflat).sum()
		
		w = classWeights[c]
		up = (2. * intersection + smooth)
		down = (iflat.sum() + tflat.sum() + smooth)
		loss += w * (1 - up / down)
	return loss

class Semantic(MapNode):
	def __init__(self, semanticClasses: Union[int, List[str]], semanticColors: List[Tuple[int, int, int]], \
			name: str="semantic", useGlobalMetrics: bool=False, criterionType: str="cross_entropy"):

		if isinstance(semanticClasses, int):
			from ..utils import logger
			logger.debug("Semantic classes were not provided, just the number. Creating fake classes.")
			semanticClasses = list(range(semanticClasses))
		assert isinstance(semanticClasses, (list, tuple))

		super().__init__(name=name, numDims=len(semanticClasses))
		self.semanticClasses = semanticClasses
		self.semanticColors = semanticColors
		self.numClasses = len(semanticClasses)
		self.useGlobalMetrics = useGlobalMetrics
		self.criterionType = criterionType
		assert len(self.semanticClasses) == len(self.semanticColors), f"{self.semanticClasses} " + \
			f"({len(self.semanticClasses)}) vs {self.semanticColors} ({len(self.semanticColors)})"

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		metrics = {
			"Accuracy" : lambda y, t: accuracy(y.argmax(-1), t.argmax(-1)),
		}
		assert not self.useGlobalMetrics
		return metrics

	@overrides
	def getNodeCriterion(self) -> CriterionType:
		criterion = {
			"cross_entropy": Semantic.cross_entropy,
			"cross_entropy_plus_dice": partial(Semantic.cross_entropy_plus_dice, nClasses=self.numClasses),
		}[self.criterionType]
		return criterion

	@staticmethod
	def cross_entropy(y, t):
		return softmax_nll(y, t, dim=-1).mean()

	@staticmethod
	def cross_entropy_plus_dice(y, t, nClasses):
		cross_entropy = softmax_nll(y, t, dim=-1).mean()
		dice = dice_loss(y, t, nClasses)
		return cross_entropy + dice
