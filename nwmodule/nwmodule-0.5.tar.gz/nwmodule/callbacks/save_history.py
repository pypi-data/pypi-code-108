import os
import numpy as np
from overrides import overrides
from typing import Any, Dict
from pathlib import Path
from .callback import Callback, CallbackName
from ..logger import logger

class SaveHistory(Callback):
	def __init__(self, fileName, **kwargs):
		self.fileName = fileName
		super().__init__(**kwargs)

	@overrides
	def onEpochStart(self, model, workingDirectory:Path, isTraining:bool):
		pass

	@overrides
	def onEpochEnd(self, model, epochResults:Dict[CallbackName, Any], workingDirectory:Path, isTraining:bool):
		if not isTraining:
			logger.debug("SaveHistory called with isTraining set to False. Returning.")
			return

		filePath = workingDirectory / self.fileName
		file = open(filePath, "w")
		Str = model.summary()
		Str += "\n\n[Train history]"
		epoch = len(model.getTrainHistory())
		for i in range(epoch):
			Str += "\nEpoch %d:" % (i + 1)
			X = model.getTrainHistory()[i]
			for k in X:
				Str += "\n- %s: %s" % (k, X[k])
		file.write(Str)
		file.close()

	@overrides
	def onCallbackSave(self, **kwargs):
		pass

	@overrides
	def onCallbackLoad(self, additional, **kwargs):
		pass

	@overrides
	def onIterationStart(self, **kwargs):
		pass

	@overrides
	def onIterationEnd(self, results:np.ndarray, labels:np.ndarray, **kwargs) -> np.ndarray:
		pass

	@overrides
	def __str__(self):
		return "SaveHistory (File: %s)" % (self.fileName)