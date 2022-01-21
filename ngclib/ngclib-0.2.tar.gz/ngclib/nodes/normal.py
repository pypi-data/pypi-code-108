import numpy as np
import torch
import torch.nn.functional as F
from nwmodule import CriterionType
from torchmetrics import Metric
from typing import Dict
from overrides import overrides

from .map_node import MapNode

class Normal(MapNode):
	def __init__(self, name: str = "normal"):
		super().__init__(name = name, numDims = 3)

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		return {
			"Normal-v1 (deg)": Normal.degreeMetricV1,
			"Normal-v2 (deg)": Normal.degreeMetricV2,
			"Normal (deg)": Normal.degreeMetric,
		}

	@overrides
	def getNodeCriterion(self) -> CriterionType:
		return Normal.lossFn

	@staticmethod
	def degreeMetricV1(y, t, **k):
		# First, remove sign from both and then do the L1 diff
		y = np.abs(y)
		t = np.abs(t)
		diff = np.abs(y - t)
		return diff.mean() * 360

	@staticmethod
	def degreeMetricV2(y, t, **k):
		# First, remove sign from both and then do the L1 diff
		y = np.abs(y)
		t = np.abs(t)
		y = torch.from_numpy(y)
		t = torch.from_numpy(t)
		cosine_distance = F.cosine_similarity(y, t)
		cosine_distance = np.minimum(np.maximum(cosine_distance.cpu().numpy(), -1.0), 1.0)
		angles = np.arccos(cosine_distance) / np.pi * 180.0
		return angles.mean()

	@staticmethod
	def degreeMetric(y, t, **k):
		# First, remove sign from both and then do the L1 diff
		y = np.abs(y)
		t = np.abs(t)
		y = torch.from_numpy(y)
		t = torch.from_numpy(t)
		cosine_distance = F.cosine_similarity(y, t, dim=-1)
		cosine_distance = cosine_distance.cpu().numpy()
		cosine_distance = np.abs(cosine_distance)
		angles = np.arccos(cosine_distance) / np.pi * 180
		angles[np.isnan(angles)] = 180
		return angles.mean()

	@staticmethod
	def lossFn(y, t):
		return ((y - t)**2).mean()