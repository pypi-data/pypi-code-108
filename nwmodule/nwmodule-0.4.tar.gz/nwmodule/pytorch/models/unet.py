import torch as tr
import torch.nn as nn
import torch.nn.functional as F
from ..layers.upsample import UpSampleLayer
from ..feed_forward_network import FeedForwardNetwork

# A simple block that implements the 2 convs + Relu layers
class UNetBlock(FeedForwardNetwork):
	def __init__(self, dIn, dOut, padding=0):
		super(UNetBlock, self).__init__()
		self.conv1 = nn.Conv2d(in_channels=dIn, out_channels=dOut, kernel_size=3, padding=padding)
		self.conv2 = nn.Conv2d(in_channels=dOut, out_channels=dOut, kernel_size=3, padding=padding)

	def forward(self, x):
		out1 = F.relu(self.conv1(x))
		out2 = F.relu(self.conv2(out1))
		return out2

# A class that implements the upsample+concatenation of the output of the downsample part with the result of the up
class UNetConcatenateBlock(FeedForwardNetwork):
	def __init__(self, dIn, dOut, upSampleType):
		super(UNetConcatenateBlock, self).__init__()
		assert upSampleType in ("conv_transposed_smooth", "conv_transposed", "nearest", "bilinear", "unpool")
		# if upSampleType in ("conv_transposed", "conv_transposed_smooth"):
		if upSampleType == "conv_transposed":
			self.upsample = UpSampleLayer(inShape=None, dIn=dIn, dOut=dIn//2, Type="conv_transposed", \
				convTransposedKernelSize=2, convTransposedStride=2, noSmoothing=True)
		elif upSampleType == "conv_transposed_smooth":
			# This one applies a secondary convolutional smoothing, which sometimes fixes checkerboard arterfacts
			self.upsample = UpSampleLayer(inShape=None, dIn=dIn, dOut=dIn//2, Type="conv_transposed", \
				convTransposedKernelSize=2, convTransposedStride=2, smoothKernelSize=5, noSmoothing=False)
		else:
			self.upsample = UpSampleLayer(inShape=None, dIn=dIn, dOut=dIn//2, Type=upSampleType)

	def forward(self, y_down, x):
		# As example y_down:(64x64), x:(28x28), out_upsample:(56x56), so we need to cut ((64 - 56)/2) = 4 on each side
		out_upsample = self.upsample(x)
		# This should be 4 each in the example
		diffH, diffW = (y_down.shape[2] - out_upsample.shape[2]) // 2, (y_down.shape[3] - out_upsample.shape[3]) // 2
		# This should the slice of (56x56)
		y_down_view = y_down[:, :, diffH : -diffH, diffW : -diffW]
		# This should concatenate both (56x56) sides on the first (features), not minibatch: (MB x 2*D x 56 x 56)
		out_cat = tr.cat([y_down_view, out_upsample], dim=1)
		return out_cat

# Implementation of the UNet model from https://arxiv.org/abs/1505.04597
class UNet(FeedForwardNetwork):
	def __init__(self, dIn, dOut, upSampleType):
		super(ModelUNet, self).__init__()
		assert upSampleType in ("bilinear", "nearest", "conv_transposed", "conv_transposed_smooth")

		self.dIn = dIn
		self.dOut = dOut

		self.pool22 = nn.MaxPool2d(kernel_size=2)
		# Downsample part
		self.block1 = UNetBlock(dIn=dIn, dOut=64)
		self.block2 = UNetBlock(dIn=64, dOut=128)
		self.block3 = UNetBlock(dIn=128, dOut=256)
		self.block4 = UNetBlock(dIn=256, dOut=512)
		# Middle part - standard architecture
		self.block5 = UNetBlock(dIn=512, dOut=1024)
		# Upsample part
		self.upconcat6 = UNetConcatenateBlock(dIn=1024, dOut=1024, upSampleType=upSampleType)
		self.block6 = UNetBlock(dIn=1024, dOut=512)
		self.upconcat7 = UNetConcatenateBlock(dIn=512, dOut=512, upSampleType=upSampleType)
		self.block7 = UNetBlock(dIn=512, dOut=256)
		self.upconcat8 = UNetConcatenateBlock(dIn=256, dOut=256, upSampleType=upSampleType)
		self.block8 = UNetBlock(dIn=256, dOut=128)
		self.upconcat9 = UNetConcatenateBlock(dIn=128, dOut=128, upSampleType=upSampleType)
		self.block9 = UNetBlock(dIn=128, dOut=64)
		self.conv10 = nn.Conv2d(in_channels=64, out_channels=dOut, kernel_size=1)

	def forward(self, x):
		# Move depth first (MB, H, W, 3) => (MB, 3, H, W)
		x = tr.transpose(tr.transpose(x, 1, 3), 2, 3)

		out1 = self.block1(x)
		out2 = self.block2(self.pool22(out1))
		out3 = self.block3(self.pool22(out2))
		out4 = self.block4(self.pool22(out3))

		out5 = self.block5(self.pool22(out4))

		in6 = self.upconcat6(out4, out5)
		out6 = self.block6(in6)
		in7 = self.upconcat7(out3, out6)
		out7 = self.block7(in7)
		in8 = self.upconcat8(out2, out7)
		out8 = self.block8(in8)
		in9 = self.upconcat9(out1, out8)
		out9 = self.block9(in9)

		out10 = self.conv10(out9)
		# (MB, D, H, W) => (MB, H, W, D)
		out10 = tr.transpose(tr.transpose(out10, 1, 3), 1, 2)
		return out10
