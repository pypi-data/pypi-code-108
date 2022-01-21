import sys
import numpy as np
from typing import Union, Tuple, Optional, Dict, Any
from overrides import overrides
from pathlib import Path

from .callback import Callback
from .callback_name import CallbackName
from ..logger import logger

# TODO: add format to saving files
# Note: This callback should be called after all (relevant) callbacks were called, otherwise we risk of storing a model
#  that hasn't updated all it's callbacks. This is relevant, for example in EarlyStopping, where we'd save the state
#  of the N-1th epoch instead of last, causing it to lead to different behavioiur pre/post loading.
class SaveModels(Callback):
	def __init__(self, mode:str, metricName:str, **kwargs):
		assert mode in ("all", "improvements", "last", "best")
		self.mode = mode
		if isinstance(metricName, Callback):
			metricName = metricName.getName()
		self.metricName = CallbackName(metricName)
		self.best = None
		super().__init__(**kwargs)

	def saveImprovements(self, model, metric, score, epoch, workingDirectory):
		if self.best is None:
			direction = metric.getDirection()
			extremes = metric.getExtremes()
			self.best = {
				"max" : extremes["min"],
				"min" : extremes["max"]
			}[direction]

		compareResult = self.metric.compareFunction(score, self.best)
		if compareResult == False:
			logger.debug("Epoch %d. Metric %s did not improve best score %s with %s" % \
				(epoch, metricName, self.best, score))
			return

		logger.debug("Epoch %d. Metric %s improved best score from %s to %s" % \
			(epoch, metricName, self.best, score))
		self.best = score
		model.saveModel(workingDirectory / \
			("model_improvement_%s_epoch-%d_score-%s" % (self.metricName, epoch, score)))

	def saveBest(self, model, metric, score, epoch, workingDirectory):
		if self.best is None:
			direction = metric.getDirection()
			extremes = metric.getExtremes()
			self.best = {
				"max" : extremes["min"],
				"min" : extremes["max"]
			}[direction]

		compareResult = metric.compareFunction(score, self.best)
		if compareResult == False:
			logger.debug("Epoch %d. Metric %s did not improve best score %s with %s" % \
				(epoch, self.metricName, self.best, score))
			return

		logger.debug("Epoch %d. Metric %s improved best score from %s to %s" % \
			(epoch, self.metricName, self.best, score))
		self.best = score
		model.saveModel(workingDirectory / ("model_best_%s.pkl" % self.metricName))

	def saveLast(self, model, metric, score, epoch, workingDirectory):
		model.saveModel(workingDirectory / "model_last.pkl")
		logger.debug("Epoch %d. Saved last model." % epoch)

	# Saving by best train loss is validation is not available, otherwise validation. Nasty situation can occur if one
	#  epoch there is a validation loss and the next one there isn't, so we need formats to avoid this and error out
	#  nicely if the format asks for validation loss and there's not validation metric reported.
	@overrides
	def onEpochEnd(self, model, epochResults:Dict[CallbackName, Any], workingDirectory:Path, isTraining:bool):
		if not isTraining:
			return
		epochResults = epochResults["Validation"] if "Validation" in epochResults else epochResults["Train"]
		epoch = len(model.getTrainHistory())
		metric = model.getMetric(self.metricName)
		score = epochResults[metric.name]
		score = score.mean() if isinstance(score, np.ndarray) else score

		f = {
			"improvements" : self.saveImprovements,
			"best" : self.saveBest,
			"last" : self.saveLast
		}[self.mode]
		f(model, metric, score, epoch, workingDirectory)

	@overrides
	def onEpochStart(self, model, workingDirectory:Path, isTraining:bool):
		assert self.metricName.name in model.getMetrics(), "Metric '%s' not in model metrics: %s" % \
			(self.metricName, list(model.getMetrics().keys()))

	@overrides
	def onIterationStart(self, **kwargs):
		pass

	@overrides
	def onIterationEnd(self, results:np.ndarray, labels:np.ndarray, **kwargs) -> np.ndarray:
		pass

	@overrides
	def onCallbackLoad(self, additional, **kwargs):
		pass

	@overrides
	def onCallbackSave(self, **kwargs):
		pass

	@overrides
	def __str__(self):
		return "SaveModels (Metric: %s. Type: %s)" % (str(self.metricName), self.mode)