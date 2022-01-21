from torchmetrics import Metric
from typing import Dict
from overrides import overrides

from .map_node import MapNode
from .normal import Normal

class CameraNormal(Normal):
	def __init__(self, name: str="cameranormal"):
		MapNode.__init__(self, name=name, numDims=3)

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		metrics = super().getNodeMetrics()
		newMetrics = {}
		for metricName, metricFn in metrics.items():
			newMetricName = metricName.replace("Normal", "CameraNormal")
			newMetrics[newMetricName] = metricFn
		return newMetrics