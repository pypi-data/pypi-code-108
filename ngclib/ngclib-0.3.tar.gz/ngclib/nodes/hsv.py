from typing import Dict
from overrides import overrides
from torchmetrics import Metric

from .map_node import MapNode
from .rgb import RGB

class HSV(RGB):
	def __init__(self, name: str = "hsv"):
		MapNode.__init__(self, name=name, numDims=3)

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		metrics = super().getNodeMetrics()
		newMetrics = {}
		for metricName, metricFn in metrics.items():
			newMetricName = metricName.replace("RGB", "HSV")
			newMetrics[newMetricName] = metricFn
		return newMetrics