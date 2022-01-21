import sys
import numpy as np
import torch as tr
import torch.nn as nn
import torch.optim as optim
from overrides import overrides
from functools import partial

from ..nwmodule import NWModule, CriterionType

def BCE(y, t):
	return -(t * tr.log(y + 1e-5) + (1 - t) * tr.log(1 - y + 1e-5)).mean()

def latentLossFn(y, t):
	encoderMean, encoderStd = y["encoder"]
	# KL-Divergence between two Gaussians: N(0, I) and N(encoderMean, encoderStd) 
	KL = 0.5 * tr.sum((encoderStd**2 + encoderMean**2 - 1 - tr.log(encoderStd**2)))
	return KL
	
def decoderLossFn(y, t):
	outputDecoder = y["decoder"]
	MB = len(y["decoder"])
	outputDecoder = outputDecoder.view(MB, -1)
	t = t.view(MB, -1)
	decoderLoss = BCE(outputDecoder, t)
	return decoderLoss

def f(y, t, weights):
	latentLoss = latentLossFn(y, t)
	decoderLoss = decoderLossFn(y, t)
	L = weights["latent"] * latentLoss + weights["decoder"] * decoderLoss
	return L

class VariationalAutoencoderNetwork(NWModule):
	def __init__(self, encoder:NWModule, decoder:NWModule, lossWeights = {"latent" : 1, "decoder" : 1}):
		super().__init__()
		assert hasattr(encoder, "noiseSize")
		assert hasattr(decoder, "noiseSize")
		self.encoder = encoder
		self.decoder = decoder
		self.lossWeights = lossWeights

	@overrides
	def getCriterion(self) -> CriterionType:
		return partial(f, weights=self.lossWeights)

	@overrides
	def networkAlgorithm(self, trInputs, trLabels, isTraining, isOptimizing):
		MB = len(trInputs)

		# Get the mean/std of this input
		encoderMean, encoderStd = self.encoder(trInputs)

		# "Reparametrization trick": Sample from N(0, I) and multiply by our distribution's mean/std.
		zNoise = tr.randn(MB, self.encoder.noiseSize).to(self.getDevice())
		zNoise = zNoise * encoderStd + encoderMean

		# Decode the result
		outputDecoder = self.decoder(zNoise)

		trResults = {
			"encoder" : (encoderMean, encoderStd),
			"decoder" : outputDecoder
		}

		trLoss = self.getCriterion()(trResults, trLabels)
		self.updateOptimizer(trLoss, isTraining, isOptimizing)
		return trResults, trLoss