import torch as tr
import numpy as np
from nwmodule import CriterionType
from torchmetrics import Metric
from typing import Dict
from overrides import overrides
from functools import partial

from .map_node import MapNode

class Depth(MapNode):
	def __init__(self, maxDepthMeters:float, name:str="depth"):
		self.maxDepthMeters = maxDepthMeters
		hyperParameters = {"maxDepthMeters":maxDepthMeters}
		super().__init__(name = name, numDims = Depth.numDims(), hyperParameters = hyperParameters)

	@staticmethod
	def numDims() -> int:
		return 1

	@overrides
	def getNodeMetrics(self) -> Dict[str, Metric]:
		metrics = {
			"Depth (m)" : partial(Depth.depthMetric, maxDepthMeters=self.maxDepthMeters, gtKey=self.name),
			"RMSE" : partial(Depth.rmseMetric, maxDepthMeters=self.maxDepthMeters, gtKey=self.name)
		}
		return metrics

	@overrides
	def getNodeCriterion(self) -> CriterionType:
		return lambda y, t: Depth.lossFn(y, t)

	@staticmethod
	def lossFn(y: tr.Tensor, t: tr.Tensor):
		assert y.shape == t.shape
		L = ((y - t)**2).mean()
		return L

	def depthMetric(y: np.ndarray, t: np.ndarray, maxDepthMeters: float, **k) -> float:
		# Normalize back to meters, output is in [0 : 1] representing [0 : maxDepthMeters]m
		yDepthMeters = y * maxDepthMeters
		tDepthMeters = t * maxDepthMeters
		l1 = np.abs(yDepthMeters - tDepthMeters).mean()
		return l1

	def rmseMetric(y: np.ndarray, t: np.ndarray, maxDepthMeters: float, **k) -> float:
		# Normalize back to milimeters, output is in [0 : 1] representing [0 : maxDepthMeters]m
		yDepthMeters = y * maxDepthMeters
		tDepthMeters = t * maxDepthMeters
		L2 = (yDepthMeters - tDepthMeters) ** 2
		rmse = np.sqrt(L2.mean())
		return rmse
