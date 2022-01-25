from typing import Dict
from overrides import overrides
from torchmetrics import Metric

from .rgb import RGB
from .map_node import MapNode

class Edges(RGB):
	def __init__(self, name:str="edges"):
		MapNode.__init__(self, name=name, numDims=1)

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		metrics = super().getNodeMetrics()
		newMetrics = {}
		for metricName, metricFn in metrics.items():
			newMetricName = metricName.replace("RGB", "Edges")
			newMetrics[newMetricName] = metricFn
		return newMetrics
