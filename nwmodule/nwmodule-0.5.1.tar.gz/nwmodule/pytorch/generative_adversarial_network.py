import sys
import numpy as np
import torch as tr
import torch.nn as nn
import torch.optim as optim
from datetime import datetime
from overrides import overrides
from collections import OrderedDict

from ..nwmodule import NWModule
from ..metrics import Loss

def bce(y, t):
	return -(t * tr.log(y + 1e-5) + (1 - t) * tr.log(1 - y + 1e-5)).mean()

class GANOptimizer(optim.Optimizer):
	def __init__(self, model, optimizer, **kwargs):
		self.model = model
		model.generator.setOptimizer(optimizer, **kwargs)
		model.discriminator.setOptimizer(optimizer, **kwargs)

	def state_dict(self):
		return {
			"discriminator" : self.model.discriminator.getOptimizer().state_dict(),
			"generator" : self.model.generator.getOptimizer().state_dict()
		}

	def load_state_dict(self, state):
		self.model.discriminator.getOptimizer().load_state_dict(state["discriminator"])
		self.model.generator.getOptimizer().load_state_dict(state["generator"])

	@overrides
	def step(self, closure=None):
		self.model.discriminator.getOptimizer().step(closure)
		self.model.generator.getOptimizer().step(closure)

	@overrides
	def __str__(self):
		Str = "[Gan Optimizer]"
		Str += "\n - Generator: %s" % self.model.generator.getOptimizerStr()
		Str += "\n - Discriminator: %s" % self.model.discriminator.getOptimizerStr()
		return Str

	def __getattr__(self, key):
		assert key in ("discriminator", "generator", "param_groups")
		if key == "param_groups":
			for pg in self.model.generator.getOptimizer().param_groups:
				yield pg
			for pg in self.model.discriminator.getOptimizer().param_groups:
				yield pg
		else:
			return self.state_dict()[key]

class GenerativeAdversarialNetwork(NWModule):
	def __init__(self, generator:NWModule, discriminator:NWModule):
		super().__init__()
		assert hasattr(generator, "noiseSize")
		self.generator = generator
		self.discriminator = discriminator

	@overrides
	def clearCallbacks(self):
		self.callbacks = OrderedDict({})
		self.addMetric("Loss", Loss())
		self.addMetrics({
			"GLoss" : lambda y, t, **k : y["gLoss"],
			"DLoss" : lambda y, t, **k : y["dLoss"]
		})

	@overrides
	def setOptimizer(self, optimizer, **kwargs):
		assert not isinstance(optimizer, optim.Optimizer)
		ganOptimizer = GANOptimizer(self, optimizer, **kwargs)
		super().setOptimizer(ganOptimizer, **kwargs)

	@overrides
	def networkAlgorithm(self, trInputs, trLabels, isTraining, isOptimizing):
		# Generate fake data
		g = self.generator.forward(trInputs)

		# Discriminator step
		dFakePredict = self.discriminator.forward(g.detach())
		dRealPredict = self.discriminator.forward(trLabels)
		MB = len(dFakePredict)
		device = self.getDevice()
		ones = tr.full((MB, ), 1, dtype=tr.float32).to(device)
		zeros = tr.full((MB, ), 0, dtype=tr.float32).to(device)
		dRealLoss = bce(dRealPredict, ones)
		dFakeLoss = bce(dFakePredict, zeros)
		dLoss = (dRealLoss + dFakeLoss) / 2
		self.discriminator.updateOptimizer(dLoss, isTraining, isOptimizing)

		# Generator step
		gFakePredict = self.discriminator.forward(g)
		gLoss = bce(gFakePredict, ones)
		self.generator.updateOptimizer(gLoss, isTraining, isOptimizing)

		trLoss = (dLoss + gLoss) / 2
		trResults = {
			"gLoss" : gLoss.detach(),
			"dLoss" : dLoss.detach(),
			"gSample" : g.detach()
		}
		return trResults, trLoss