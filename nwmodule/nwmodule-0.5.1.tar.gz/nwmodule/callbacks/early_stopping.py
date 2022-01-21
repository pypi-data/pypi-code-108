import sys
import numpy as np
from pathlib import Path
from typing import Dict
from .callback import Callback
from .callback_name import CallbackName
from ..logger import logger

# TODO: Remove mode from ctor and infer at epoch end.
class EarlyStopping(Callback):
	def __init__(self, metricName:str="Loss", min_delta:float=0, patience:float=10, percentage:bool=False):
		self.metricName = CallbackName(metricName)
		self.min_delta = min_delta
		self.patience = patience
		self.percentage = percentage
		super().__init__()

		self.bestMetricScore = None
		self.numBadEpochs = 0
		self.metricDirection = None

	def onEpochStart(self, model, workingDirectory:Path, isTraining:bool):
		pass

	def onIterationStart(self, **kwargs):
		pass

	def onIterationEnd(self, results:np.ndarray, labels:np.ndarray, **kwargs) -> np.ndarray:
		pass

	def onEpochEnd(self, model, epochResults:Dict, workingDirectory:Path, isTraining:bool):
		Key = "Validation" if "Validation" in epochResults else "Train"
		score = epochResults[Key][self.metricName]
		assert not np.isnan(score)

		# First epoch we need to get some value running.
		if self.bestMetricScore is None:
			assert hasattr(model, "finished")
			self.numBadEpochs = 0
			self.bestMetricScore = score
			self.metricDirection = model.getMetrics()[self.metricName].getDirection()
			assert self.metricDirection in ("min", "max")
			return

		fIsBetter = EarlyStopping._init_is_better(self.metricDirection, self.patience, self.percentage, self.min_delta)
		if fIsBetter(score, self.bestMetricScore):
			self.numBadEpochs = 0
			self.bestMetricScore = score
		else:
			self.numBadEpochs += 1
			logger.debug("Early Stopping is being applied. Num bad in a row: %d. Patience: %d" % \
				(self.numBadEpochs, self.patience))

		if self.numBadEpochs >= self.patience:
			logger.debug("Num bad epochs in a row: %d. Stopping the training!" % self.numBadEpochs)
			model.finished = True

	def _init_is_better(metricDirection, patience, modePercentage, minDelta):
		if patience == 0:
			return lambda a, best: True
		fDirection = lambda a, b, c : (a < b - c if metricDirection == "min" else a > b + c)
		if modePercentage:
			minDelta = best * minDelta / 100
		return lambda a, best : fDirection(a, best, minDelta)

	def __str__(self):
		return "EarlyStopping (Metric: %s. Min delta: %2.2f. Patience: %d. Percentage: %s)" \
			% (self.metricName, self.min_delta, self.patience, self.percentage)