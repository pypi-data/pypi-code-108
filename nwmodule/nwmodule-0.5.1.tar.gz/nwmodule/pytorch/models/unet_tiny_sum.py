import torch.nn as nn
import torch.nn.functional as F
from ..feed_forward_network import FeedForwardNetwork

class UNetTinySum(FeedForwardNetwork):
	def __init__(self, dIn, dOut, numFilters):
		super().__init__()

		# Model parameters
		NF = numFilters
		self.down1 = nn.Conv2d(in_channels=dIn, out_channels=NF, kernel_size=3, padding=1)
		self.down1pool = nn.Conv2d(in_channels=NF, out_channels=NF, kernel_size=3, padding=1, stride=2)
		self.down2 = nn.Conv2d(in_channels=NF, out_channels=NF * 2, kernel_size=3, padding=1)
		self.down2pool = nn.Conv2d(in_channels=NF * 2, out_channels=NF * 2, kernel_size=3, padding=1, stride=2)
		self.down3 = nn.Conv2d(in_channels=NF * 2, out_channels=NF * 4, kernel_size=3, padding=1)
		self.down3pool = nn.Conv2d(in_channels=NF * 4, out_channels=NF * 4, kernel_size=3, padding=1, stride=2)

		# stacked dilated conv
		self.dilate1 = nn.Conv2d(in_channels=NF * 4, out_channels=NF * 8, kernel_size=3, padding=1, dilation=1)
		self.dilate2 = nn.Conv2d(in_channels=NF * 8, out_channels=NF * 8, kernel_size=3, padding=2, dilation=2)
		self.dilate3 = nn.Conv2d(in_channels=NF * 8, out_channels=NF * 8, kernel_size=3, padding=4, dilation=4)
		self.dilate4 = nn.Conv2d(in_channels=NF * 8, out_channels=NF * 8, kernel_size=3, padding=8, dilation=8)
		self.dilate5 = nn.Conv2d(in_channels=NF * 8, out_channels=NF * 8, kernel_size=3, padding=16, dilation=16)
		self.dilate6 = nn.Conv2d(in_channels=NF * 8, out_channels=NF * 8, kernel_size=3, padding=32, dilation=32)

		self.up3_tr = nn.ConvTranspose2d(in_channels=NF * 8, out_channels=NF * 4, kernel_size=3, stride=2, padding=1)
		self.up3 = nn.Conv2d(in_channels=NF * 4, out_channels=NF * 4, kernel_size=3, padding=1)
		self.up2_tr = nn.ConvTranspose2d(in_channels=NF * 4, out_channels=NF * 2, kernel_size=3, stride=2, padding=1)
		self.up2 = nn.Conv2d(in_channels=NF * 2, out_channels=NF * 2, kernel_size=3, padding=1)
		self.up1_tr = nn.ConvTranspose2d(in_channels=NF * 2, out_channels=NF, kernel_size=3, stride=2, padding=1)
		self.up1 = nn.Conv2d(in_channels=NF, out_channels=NF, kernel_size=3, padding=1)
		self.finalConv = nn.Conv2d(in_channels=NF, out_channels=dOut, kernel_size=(1, 1))

	def forward(self, x):
		y1 = F.relu(self.down1(x))
		y1_pool = F.relu(self.down1pool(y1))
		y2 = F.relu(self.down2(y1_pool))
		y2_pool = F.relu(self.down2pool(y2))
		y3 = F.relu(self.down3(y2_pool))
		y3_pool = F.relu(self.down3pool(y3))

		y_dilate1 = F.relu(self.dilate1(y3_pool))
		y_dilate2 = F.relu(self.dilate2(y_dilate1))
		y_dilate3 = F.relu(self.dilate3(y_dilate2))
		y_dilate4 = F.relu(self.dilate4(y_dilate3))
		y_dilate5 = F.relu(self.dilate5(y_dilate4))
		y_dilate6 = F.relu(self.dilate6(y_dilate5))
		y_dilate_sum = y_dilate1 + y_dilate2 + y_dilate3 + y_dilate4 + y_dilate5 + y_dilate6

		# Skip and padding for residual connection
		def f(up_tr, y_up, y_down, up):
			y = F.relu(up_tr(y_up))
			diffUp, diffLeft = y_down.shape[-2] - y.shape[-2], y_down.shape[-1] - y.shape[-1]
			yPad = F.pad(y, (0, diffLeft, 0, diffUp))
			y_up_tr = yPad + y_down
			y_up = F.relu(up(y_up_tr))
			return y_up

		y_up3 = f(self.up3_tr, y_dilate_sum, y3, self.up3)
		y_up2 = f(self.up2_tr, y_up3, y2, self.up2)
		y_up1 = f(self.up1_tr, y_up2, y1, self.up1)
		y_final = self.finalConv(y_up1)
		return y_final