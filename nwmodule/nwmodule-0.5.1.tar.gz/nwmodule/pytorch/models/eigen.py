import torch as tr
import torch.nn as nn
import torch.nn.functional as F
from ..feed_forward_network import FeedForwardNetwork

# The top architeture in the original paper.
class ModelDepthCoarse(FeedForwardNetwork):
	def __init__(self):
		super().__init__()
		self.conv1 = nn.Conv2d(in_channels=3, out_channels=96, kernel_size=11, stride=4)
		self.conv2 = nn.Conv2d(in_channels=96, out_channels=256, kernel_size=5, stride=1)
		self.conv3 = nn.Conv2d(in_channels=256, out_channels=384, kernel_size=3, stride=1)
		self.conv4 = nn.Conv2d(in_channels=384, out_channels=384, kernel_size=3, stride=1)
		self.conv5 = nn.Conv2d(in_channels=384, out_channels=256, kernel_size=3, stride=1)
		self.fc1 = nn.Linear(256 * 6 * 11, 4096)
		self.fc2 = nn.Linear(4096, 55 * 74)
		self.pool22 = nn.MaxPool2d(2, 2)
		self.dropout_fc1 = nn.Dropout(p=0.2)

	def forward(self, x):
		x = tr.transpose(tr.transpose(x, 1, 3), 2, 3) # Move depth first
		coarse1 = self.pool22(F.relu(self.conv1(x)))
		coarse2 = self.pool22(F.relu(self.conv2(coarse1)))
		coarse3 = F.relu(self.conv3(coarse2))
		coarse4 = F.relu(self.conv4(coarse3))
		coarse5 = F.relu(self.conv5(coarse4))
		coarse5 = coarse5.view(-1, 256 * 6 * 11)
		coarse6 = F.relu(self.dropout_fc1(self.fc1(coarse5)))
		coarse7 = self.fc2(coarse6)
		# coarse7 (MB, 55 * 74) => (MB, 55, 74)
		coarse7 = coarse7.view(-1, 55, 74)
		return coarse7

class ModelDepthFine(FeedForwardNetwork):
	def __init__(self):
		super().__init__()
		self.conv1 = nn.Conv2d(in_channels=3, out_channels=63, kernel_size=9, stride=2)
		self.conv2 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=5, stride=1)
		self.conv3 = nn.Conv2d(in_channels=64, out_channels=1, kernel_size=5, stride=1)
		self.pool22 = nn.MaxPool2d(2, 2)

	def forward(self, x, y_coarse):
		x = tr.transpose(tr.transpose(x, 1, 3), 2, 3)
		# Coarse output is (MB, 55, 74) => (MB, 1, 55, 74) => pad to (MB, 1, 58, 78)
		y_coarse = F.pad(y_coarse.view(-1, 1, 55, 74), (2, 2, 1, 2), "reflect")
		fine1 = self.pool22(F.relu(self.conv1(x)))
		fine2 = tr.cat((fine1, y_coarse), dim=1)
		fine3 = F.relu(self.conv2(fine2))
		fine4 = self.conv3(fine3)
		# fine4 (MB, 1, 50, 70) => (MB, 50, 70)
		fine4 = fine4.view(fine4.shape[0], fine4.shape[2], fine4.shape[3])
		return fine4

# Implementation of the Eigen model from https://arxiv.org/abs/1406.2283
class Eigen(FeedForwardNetwork):
	def __init__(self,  coarseOnly):
		super().__init__()
		self.coarseOnly = coarseOnly
		self.coarse = ModelDepthCoarse()
		if not self.coarseOnly:
			self.fine = ModelDepthFine()

	def __str__(self):
		return "Eigen. Coarse only: %s." % (self.coarseOnly)

	def forward(self, x):
		coarseForward = self.coarse.forward(x)
		if self.coarseOnly:
			return coarseForward
		else:
			fineForward = self.fine.forward(x, coarseForward)
			return fineForward
