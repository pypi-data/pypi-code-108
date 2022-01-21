from typing import Dict
from overrides import overrides
from torchmetrics import Metric

from .map_node import MapNode
from .rgb import RGB

class Halftone(RGB):
	def __init__(self, name:str="halftone"):
		MapNode.__init__(self, name=name, numDims=3)

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		metrics = super().getNodeMetrics()
		newMetrics = {}
		for metricName, metricFn in metrics.items():
			newMetricName = metricName.replace("RGB", "Halftone")
			newMetrics[newMetricName] = metricFn
		return newMetrics