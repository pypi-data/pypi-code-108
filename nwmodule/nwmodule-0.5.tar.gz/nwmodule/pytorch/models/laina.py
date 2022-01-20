import torch as tr
import torch.nn as nn
import torch.nn.functional as F

from ..layers.upsample import UpSampleLayer
from ..feed_forward_network import FeedForwardNetwork

# Implementation of the Laina model from https://arxiv.org/abs/1606.00373
class Laina(FeedForwardNetwork):
	def __init__(self, baseModelType, upSampleType, baseModelPreTrained):
		super().__init__()
		assert baseModelType in ("resnet50", )
		assert upSampleType in ("unpool", "bilinear", "nearest", "conv_transposed")
		self.baseModelType = baseModelType
		self.upSampleType = upSampleType
		self.baseModelPreTrained = baseModelPreTrained

		if self.baseModelType == "resnet50":
			assert False, "TODO"
			# self.baseModel = ResNet50NoTop(pretrained=baseModelPreTrained)

		upsampleArgs = {}
		if upSampleType == "conv_transposed":
			upsampleArgs = {
				"noSmoothing" : False,
				"convTransposedKernelSize" : 2,
				"convTransposedStride" : 2
			}

		self.conv_3_1 = nn.Conv2d(in_channels=2048, out_channels=1024, kernel_size=1)
		self.bn_3_1 = nn.BatchNorm2d(1024)
		self.upConv_3_2 = UpSampleLayer(dIn=1024, dOut=512, Type=upSampleType, **upsampleArgs)
		self.upConv_3_3 = UpSampleLayer(dIn=512, dOut=256, Type=upSampleType, **upsampleArgs)
		self.upConv_3_4 = UpSampleLayer(dIn=256, dOut=128, Type=upSampleType, **upsampleArgs)
		self.upConv_3_5 = UpSampleLayer(dIn=128, dOut=64, Type=upSampleType, **upsampleArgs)
		self.conv_3_6 = nn.Conv2d(in_channels=64, out_channels=1, kernel_size=3)

	def __str__(self):
		return "Laina. Base model: %s (%spretrained). Upsample type: %s" % \
			(self.baseModelType, ("" if self.baseModelPreTrained else "not "), self.upSampleType)

	def forward(self, x):
		# Move depth first (MB, 228, 304, 3) => (MB, 3, 228, 304)
		x = tr.transpose(tr.transpose(x, 1, 3), 2, 3)

		# Output of ResNet-50 is (MB, 2048, 8, 10), now we just add the 3rd row in the paper
		y_base = self.baseModel(x)

		# 3rd row of paper
		y_3_1 = F.relu(self.bn_3_1(self.conv_3_1(y_base)))
		y_3_2 = self.upConv_3_2(y_3_1)
		y_3_3 = self.upConv_3_3(y_3_2)
		y_3_4 = self.upConv_3_4(y_3_3)
		y_3_5 = self.upConv_3_5(y_3_4)
		y_3_6 = F.pad(self.conv_3_6(y_3_5), (1, 1, 1, 1), "reflect")
		# y_3_6 shape = (N, 1, 128, 160) => (N, 128, 160)
		y_3_6 = y_3_6.view(y_3_6.shape[0], y_3_6.shape[2], y_3_6.shape[3])

		return y_3_6