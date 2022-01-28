import torch as tr
import numpy as np
from collections import OrderedDict

def getTrainableParameters(model):
	if not model.training:
		return {}

	trainableParameters = {}
	namedParams = dict(model.named_parameters())
	# Some PyTorch "weird" stuff. Basically this is a hack specifically for BatchNorm (Dropout not supported yet...).
	# BatchNorm parameters are not stored in named_parameters(), just in state_dict(), however in state_dict() we can't
	#  know if it's trainable or not. So, in order to keep all trainable parameters, we need to check if it's either
	#  a BN (we'll also store non-trainable BN, but that's okay) or if it's trainable (in named_params).
	def isBatchNormModuleTrainable(name):
		nonParametersNames = ["running_mean", "running_var", "num_batches_tracked"]
		if name.split(".")[-1] in nonParametersNames:
			# edges.10.model.module.0.conv7.1.running_mean => edges.10.model.module.0.conv7.1.weight is trainable?
			resName = ".".join(name.split(".")[0 : -1])
			potentialName = "%s.weight" % (resName)
			if potentialName in namedParams and namedParams[potentialName].requires_grad:
				return True
		return False

	for name in model.state_dict():
		if isBatchNormModuleTrainable(name):
			trainableParameters[name] = model.state_dict()[name]

		if (name in namedParams) and (namedParams[name].requires_grad):
			trainableParameters[name] = model.state_dict()[name]
	return trainableParameters

def computeNumParams(namedParams):
	numParams = 0
	for name in namedParams:
		param = namedParams[name]
		numParams += np.prod(param.shape)
	return numParams

def getNumParams(model):
	return computeNumParams(model.state_dict()), computeNumParams(getTrainableParameters(model))

# Results come in torch format, but callbacks require numpy, so convert the results back to numpy format
def npGetData(data):
	if data is None:
		return None
	elif isinstance(data, (int, float)):
		return np.array([data])
	elif isinstance(data, list):
		return [npGetData(x) for x in data]
	elif isinstance(data, tuple):
		return tuple(npGetData(x) for x in data)
	elif isinstance(data, set):
		return {npGetData(x) for x in data}
	elif isinstance(data, (dict, OrderedDict)):
		return {k : npGetData(data[k]) for k in data}
	elif isinstance(data, tr.Tensor):
		return data.detach().to("cpu").numpy()
	elif isinstance(data, np.ndarray):
		return data
	elif callable(data):
		return data
	elif isinstance(data, str):
		return data
	elif hasattr(data, "to_numpy"):
		return data.to_numpy()
	assert False, f"Got type {type(data)}"

# Equivalent of the function above, but using the data from generator (which comes in numpy format)
def trGetData(data):
	if data is None:
		return None
	elif isinstance(data, (np.int32, np.int8, np.int16, np.int64, np.float32, np.float64, int, float)):
		return tr.Tensor([data])
	elif isinstance(data, list):
		return [trGetData(x) for x in data]
	elif isinstance(data, tuple):
		return tuple(trGetData(x) for x in data)
	elif isinstance(data, set):
		return {trGetData(x) for x in data}
	elif isinstance(data, (dict, OrderedDict)):
		return {k : trGetData(data[k]) for k in data}
	elif isinstance(data, tr.Tensor):
		return data
	elif isinstance(data, np.ndarray):
		return tr.from_numpy(data)
	elif callable(data):
		return data
	elif isinstance(data, str):
		return data
	assert False, f"Got type {type(data)}"

def trToDevice(data, device:tr.device):
	if isinstance(data, tr.Tensor):
		return data.to(device)
	elif isinstance(data, list):
		return [trToDevice(x, device) for x in data]
	elif isinstance(data, tuple):
		return tuple(trToDevice(x, device) for x in data)
	elif isinstance(data, set):
		return {trToDevice(x, device) for x in data}
	elif isinstance(data, dict):
		return {k: trToDevice(data[k], device) for k in data}
	elif isinstance(data, OrderedDict):
		return OrderedDict({k: trToDevice(data[k], device) for k in data})
	assert False, f"Got type {type(data)}"

# Equivalent of function above but does detach()
def trDetachData(data):
	if data is None:
		return None
	elif type(data) in (list, tuple):
		return [trDetachData(x) for x in data]
	elif type(data) in (dict, OrderedDict):
		return {k : trDetachData(data[k]) for k in data}
	elif type(data) is tr.Tensor:
		return data.detach()
	assert False, "Got type %s" % (type(data))

def npToTrCall(fn, *args, **kwargs):
	return npGetData(fn(*trGetData(args), **trGetData(kwargs)))

def trToNpCall(fn, *args, **kwargs):
	return trGetData(fn(*npGetData(args), **npGetData(kwargs)))

def getOptimizerStr(optimizer):
	if isinstance(optimizer, dict):
		return ["Dict"]

	if optimizer is None:
		return ["None"]

	if isinstance(optimizer, tr.optim.SGD):
		groups = optimizer.param_groups[0]
		params = "Learning rate: %s, Momentum: %s, Dampening: %s, Weight Decay: %s, Nesterov: %s" % \
			(groups["lr"], groups["momentum"], groups["dampening"], groups["weight_decay"], groups["nesterov"])
		optimizerType = "SGD"
	elif isinstance(optimizer, (tr.optim.Adam, tr.optim.AdamW)):
		groups = optimizer.param_groups[0]
		params = "Learning rate: %s, Betas: %s, Eps: %s, Weight Decay: %s" % (groups["lr"], groups["betas"], \
			groups["eps"], groups["weight_decay"])
		optimizerType = {
			tr.optim.Adam : "Adam",
			tr.optim.AdamW : "AdamW"
		}[type(optimizer)]
	elif isinstance(optimizer, tr.optim.RMSprop):
		groups = optimizer.param_groups[0]
		params = "Learning rate: %s, Momentum: %s. Alpha: %s, Eps: %s, Weight Decay: %s" % (groups["lr"], \
			groups["momentum"], groups["alpha"], groups["eps"], groups["weight_decay"])
		optimizerType = "RMSprop"
	elif isinstance(optimizer, tr.optim.Optimizer):
		return str(optimizer)
	else:
		optimizerType = "Generic Optimizer"
		params = str(optimizer)

	return ["%s. %s" % (optimizerType, params)]
