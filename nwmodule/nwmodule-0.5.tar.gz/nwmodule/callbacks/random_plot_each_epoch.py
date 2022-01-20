import os
import numpy as np
from pathlib import Path
from typing import Callable
from overrides import overrides
from .callback import Callback

_plotFns = {}
_plotIterationFns = {}

class RandomPlotEachEpoch(Callback):
	# @param[in] Plot function that receives the 3 arguments (x, y, t) for that particular iteration
	# @param[in] baeseDir The subdirectory where the samples are created. By default it's '$(pwd)/samples/'
	# @param[in] plotIterationFn Callback to get the iteration at which the main callback is called.
	#  By default it's 0 (start of epoch).
	def __init__(self, plotFn:Callable, baseDir:str="samples", plotIterationFn=lambda : 0):
		super().__init__(name="RandomPlotEachEpoch (Dir='%s')" % baseDir)
		self.baseDir = baseDir
		self.plotFn = plotFn
		self.plotIterationFn = plotIterationFn
		self.currentEpoch = None
		self.plotIteration = None
		self.workingDirectory = None

		global _plotFns, _plotIterationFns
		_plotFns[self] = self.plotFn
		_plotIterationFns[self] = self.plotIterationFn

	@overrides
	def onEpochStart(self, model, workingDirectory:Path, isTraining:bool):
		self.currentEpoch = len(model.getTrainHistory()) + 1
		self.plotIteration = self.plotIterationFn()
		self.workingDirectory = workingDirectory

	@overrides
	def onIterationEnd(self, results:np.ndarray, labels:np.ndarray, **kwargs) -> np.ndarray:
		if kwargs["iteration"] != self.plotIteration:
			return
		if kwargs["isTraining"]:
			if kwargs["isOptimizing"]:
				Dir = "%s/%s/%d/train" % (self.workingDirectory, self.baseDir, self.currentEpoch)
			else:
				Dir = "%s/%s/%d/validation" % (self.workingDirectory, self.baseDir, self.currentEpoch)
		else:
			Dir = self.workingDirectory / self.baseDir / "test"
		Path(Dir).mkdir(exist_ok=True, parents=True)
		self.plotFn(x=kwargs["data"], y=results, t=labels, workingDirectory=Dir)

	def onCallbackLoad(self, additional, **kwargs):
		global _plotFns, _plotIterationFns
		if not self in _plotFns:
			X = tuple(filter(lambda x : isinstance(x, type(self)), kwargs["model"].getCallbacks()))
			assert len(X) == 1
			_plotFns[self] = X[0].plotFn
			_plotIterationFns[self] = X[0].plotIterationFn
		self.plotFn = _plotFns[self]
		self.plotIterationFn = _plotIterationFns[self]

	def onCallbackSave(self, **kwargs):
		self.plotFn = None
		self.plotIterationFn = None

	def onEpochEnd(self, model, epochResults, workingDirectory:Path, isTraining:bool):
		pass

	def onIterationStart(self, **kwargs):
		pass