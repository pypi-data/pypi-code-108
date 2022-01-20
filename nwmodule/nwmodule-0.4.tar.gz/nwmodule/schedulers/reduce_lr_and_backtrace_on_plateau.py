from torch.optim.lr_scheduler import _LRScheduler
from overrides import overrides
from copy import deepcopy
from ..nwmodule import NWModule
from ..callbacks import CallbackName
from ..logger import logger

class ReduceLRAndBacktrackOnPlateau(_LRScheduler):
	def __init__(self, model:NWModule, metricName:CallbackName, patience:int, factor:float):
		assert patience > 0
		self.model = model
		self.metricName = metricName
		self.patience = patience
		self.factor = factor

		self.lastRelevantWeights = self.model.serializer.doSaveWeights()
		self.lastRelevantOptimizer = self.model.getOptimizer().state_dict()
		self.currentLR = [float(pg["lr"]) for pg in self.model.getOptimizer().param_groups]
		self.metric = self.model.getMetric(self.metricName)
		self.numBadInARow = 0
		metricExtremes = self.metric.getExtremes()
		self.lastRelevantValue = metricExtremes["min"] if self.metric.getDirection() == "max" \
			else metricExtremes["max"]
		self.storedArgs = None

	def state_dict(self):
		return {
			"lastRelevantWeights" : self.lastRelevantWeights,
			"metricName" : self.metricName,
			"numBadInARow" : self.numBadInARow,
			"lastRelevantValue" : self.lastRelevantValue,
			"currentLR" : self.currentLR
		}

	def load_state_dict(self, state_dict):
		self.lastRelevantWeights = state_dict["lastRelevantWeights"]
		self.metricName = state_dict["metricName"]
		self.metric = self.model.getMetric(self.metricName)
		self.numBadInARow = state_dict["numBadInARow"]
		self.lastRelevantValue = state_dict["lastRelevantValue"]
		self.currentLR = state_dict["currentLR"]

	@overrides
	def step(self, epoch=None):
		trainHistory = self.model.trainHistory[-1]
		if "Validation" in trainHistory:
			score = self.model.trainHistory[-1]["Validation"][self.metric.getName()]
		else:
			score = self.model.trainHistory[-1]["Train"][self.metric.getName()]

		if not self.metric.compareFunction(score, self.lastRelevantValue):
			self.numBadInARow += 1
		else:
			self.lastRelevantValue = score
			self.numBadInARow = 0
			self.lastRelevantWeights = deepcopy(self.model.serializer.doSaveWeights())
			self.lastRelevantOptimizer = deepcopy(self.model.getOptimizer().state_dict())

		if self.numBadInARow == self.patience:
			logger.log(5, ("Reached %d bad epochs. Resetting to last good" + \
				" checkpoint. Old LR: %2.5f. New LR: %2.5f") % (self.numBadInARow, self.currentLR[0], \
				self.currentLR[0] / self.factor))
			self.numBadInARow = 0
			self.model.serializer.doLoadWeights(self.lastRelevantWeights)
			self.model.getOptimizer().load_state_dict(self.lastRelevantOptimizer)
			for i, param_group in enumerate(self.model.getOptimizer().param_groups):
				self.currentLR[i] /= self.factor
				param_group["lr"] = self.currentLR[i]

	def __str__(self):
		return "ReduceLRAndBacktrackOnPlateau (Patience: %d. Factor: %2.2f)" % (self.patience, self.factor)
