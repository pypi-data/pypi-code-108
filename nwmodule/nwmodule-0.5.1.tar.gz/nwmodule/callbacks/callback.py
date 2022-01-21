import numpy as np
from abc import ABC, abstractmethod
from typing import Union, Tuple, Any, Dict
from pathlib import Path
from .callback_name import CallbackName

class Callback(ABC):
	def __init__(self, name:Union[str, Tuple[Any]] = None):
		self.setName(name)

	def setName(self, name:Union[str, Tuple[Any]] = None):
		if name is None:
			name = str(self)
		self.name = CallbackName(name)

	def getName(self) -> CallbackName:
		return self.name

	# This is used by complex MetricAsCallbacks where we do some stateful computation at every iteration and we want
	#  to reduce it gracefully at the end of the epoch, so it can be stored in trainHistory, as well as for other
	#  callbacks to work nicely with it (SaveModels, PlotCallbacks, etc.). So, we apply a reduction function (default
	#  is identity, which might or might not work depending on algorithm).
	def epochReduceFunction(self, results:np.ndarray) -> np.ndarray:
		return results

	def iterationReduceFunction(self, results:np.ndarray) -> np.ndarray:
		return results

	@abstractmethod
	def onEpochStart(self, model, workingDirectory:Path, isTraining:bool):
		pass

	@abstractmethod
	def onEpochEnd(self, model, epochResults:Dict[CallbackName, Any], workingDirectory:Path, isTraining:bool):
		pass

	@abstractmethod
	def onIterationStart(self, **kwargs):
		pass

	@abstractmethod
	def onIterationEnd(self, results:np.ndarray, labels:np.ndarray, **kwargs) -> np.ndarray:
		pass

	# Some callbacks requires some special/additional tinkering when loading a neural network model from a pickle
	#  binary file (i.e scheduler callbacks must update the optimizer using the new model, rather than the old one).
	#  @param[in] additional Usually is the same as returned by onCallbackSave (default: None)
	def onCallbackLoad(self, additional, **kwargs):
		pass

	# Some callbacks require some special/additional tinkering when saving (such as closing files). It should be noted
	#  that it's safe to close files (or any other side-effect action) because callbacks are deepcopied before this
	#  method is called (in saveModel)
	def onCallbackSave(self, **kwargs):
		pass
