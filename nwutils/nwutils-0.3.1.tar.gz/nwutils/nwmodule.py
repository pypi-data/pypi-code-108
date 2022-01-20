from nwmodule import NWModule
from nwmodule.pytorch import FeedForwardNetwork

def trModuleWrapper(module):
	class Model(FeedForwardNetwork):
		def __init__(self, _module):
			super().__init__()
			self._module = _module

		def forward(self, *args, **kwargs):
			return self._module(*args, **kwargs)

	res = Model(module)
	return res

def getModelHistoryMessage(model:NWModule):
	Str = model.summary() + "\n"
	trainHistory = model.trainHistory
	for i in range(len(trainHistory)):
		Str += trainHistory[i]["message"] + "\n"
	return Str
