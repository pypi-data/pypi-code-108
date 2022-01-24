import os
import setuptools


import numpy as np
from pytorch_lightning import Trainer

import torch
import torch.nn as nn
import torch.nn.functional as F

import torchmetrics

import pytorch_lightning.loggers as pl_loggers

from lightning_nets.data import *
from lightning_nets.hooks import *
from lightning_nets.modules import *
from lightning_nets.hooks.plotters import *

from torchmetrics import *

AVAIL_GPUS = min(1, torch.cuda.device_count())
PATH_DATASETS = os.environ.get("PATH_DATASETS", ".")
BATCH_SIZE = 256
IMG_SIZE = 32

class generator(nn.Module):
    # initializers
    def __init__(self, d=128):
        super(generator, self).__init__()
        self.deconv1_1 = nn.ConvTranspose2d(100, d*2, 4, 1, 0)
        self.deconv1_1_bn = nn.BatchNorm2d(d*2)
        self.deconv1_2 = nn.ConvTranspose2d(10, d*2, 4, 1, 0)
        self.deconv1_2_bn = nn.BatchNorm2d(d*2)
        self.deconv2 = nn.ConvTranspose2d(d*4, d*2, 4, 2, 1)
        self.deconv2_bn = nn.BatchNorm2d(d*2)
        self.deconv3 = nn.ConvTranspose2d(d*2, d, 4, 2, 1)
        self.deconv3_bn = nn.BatchNorm2d(d)
        self.deconv4 = nn.ConvTranspose2d(d, 1, 4, 2, 1)
        self.onehot = torch.zeros(10, 10)
        self.onehot = self.onehot.scatter_(1, torch.LongTensor([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]).view(10,1), 1).view(10, 10, 1, 1)

        if torch.cuda.is_available():
            self.onehot = self.onehot.cuda()
        
        self.init_weights()
   
    def init_weights(self, init_type='normal', gain=0.02):
        def init_func(m):
            classname = m.__class__.__name__
            if hasattr(m, 'weight') and (classname.find('Conv') != -1 or classname.find('Linear') != -1):
                if init_type == 'normal':
                    torch.nn.init.normal_(m.weight.data, 0.0, gain)
                elif init_type == 'xavier':
                    torch.nn.init.xavier_normal_(m.weight.data, gain=gain)
                elif init_type == 'kaiming':
                    torch.nn.init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
                elif init_type == 'orthogonal':
                    torch.nn.init.orthogonal_(m.weight.data, gain=gain)
                else:
                    raise NotImplementedError('initialization method [%s] is not implemented' % init_type)
                if hasattr(m, 'bias') and m.bias is not None:
                    torch.nn.init.constant_(m.bias.data, 0.0)
            elif classname.find('BatchNorm1d') != -1:
                torch.nn.init.normal_(m.weight.data, 1.0, gain)
                torch.nn.init.constant_(m.bias.data, 0.0)
        self.apply(init_func)

    # forward method
    def forward(self, input):
        z = input[:,1:].view(-1, 100, 1, 1)
        class_labels = input[:,0].long()
        label_one_hot = self.onehot[class_labels]#F.one_hot(class_labels, num_classes=10)
        x = F.relu(self.deconv1_1_bn(self.deconv1_1(z)))
        y = F.relu(self.deconv1_2_bn(self.deconv1_2(label_one_hot)))
        x = torch.cat([x, y], 1)
        x = F.relu(self.deconv2_bn(self.deconv2(x)))
        x = F.relu(self.deconv3_bn(self.deconv3(x)))
        x = F.tanh(self.deconv4(x))
        # x = F.relu(self.deconv4_bn(self.deconv4(x)))
        # x = F.tanh(self.deconv5(x))

        return x.squeeze()

class discriminator(nn.Module):
    # initializers
    def __init__(self, d=128):
        super().__init__()
        self.conv1_1 = nn.Conv2d(1, int(d/2), 4, 2, 1)
        self.conv1_2 = nn.Conv2d(10, int(d/2), 4, 2, 1)
        self.conv2 = nn.Conv2d(d, d*2, 4, 2, 1)
        self.conv2_bn = nn.BatchNorm2d(d*2)
        self.conv3 = nn.Conv2d(d*2, d*4, 4, 2, 1)
        self.conv3_bn = nn.BatchNorm2d(d*4)
        self.conv4 = nn.Conv2d(d * 4, 1, 4, 1, 0)
        self.fill = torch.zeros([10, 10, IMG_SIZE, IMG_SIZE])
        for i in range(10):
            self.fill[i, i, :, :] = 1
        
        if torch.cuda.is_available():
            self.fill = self.fill.cuda()

        self.init_weights()
   
    def init_weights(self, init_type='normal', gain=0.02):
        def init_func(m):
            classname = m.__class__.__name__
            if hasattr(m, 'weight') and (classname.find('Conv') != -1 or classname.find('Linear') != -1):
                if init_type == 'normal':
                    torch.nn.init.normal_(m.weight.data, 0.0, gain)
                elif init_type == 'xavier':
                    torch.nn.init.xavier_normal_(m.weight.data, gain=gain)
                elif init_type == 'kaiming':
                    torch.nn.init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
                elif init_type == 'orthogonal':
                    torch.nn.init.orthogonal_(m.weight.data, gain=gain)
                else:
                    raise NotImplementedError('initialization method [%s] is not implemented' % init_type)
                if hasattr(m, 'bias') and m.bias is not None:
                    torch.nn.init.constant_(m.bias.data, 0.0)
            elif classname.find('BatchNorm1d') != -1:
                torch.nn.init.normal_(m.weight.data, 1.0, gain)
                torch.nn.init.constant_(m.bias.data, 0.0)
        self.apply(init_func)

    # forward method
    def forward(self, input, output):
        label = input[:,0].long()
        label = self.fill[label]

        if len(output.shape) == 3:
            output = torch.unsqueeze(output, dim=1)

        x = F.leaky_relu(self.conv1_1(output), 0.2)
        y = F.leaky_relu(self.conv1_2(label), 0.2)
        x = torch.cat([x, y], 1)
        x = F.leaky_relu(self.conv2_bn(self.conv2(x)), 0.2)
        x = F.leaky_relu(self.conv3_bn(self.conv3(x)), 0.2)
        x = F.sigmoid(self.conv4(x)).view(input.shape[0], 1)

        return x

csv_logger = pl_loggers.CSVLogger(save_dir=os.getcwd(), name="logs", flush_logs_every_n_steps=3)

data_module = MNISTDataModule(batch_size=BATCH_SIZE, image_size = [IMG_SIZE, IMG_SIZE], latent_size=100)

metrics = [ MeanSquaredError(), MeanSquaredError(squared=False), MeanAbsoluteError(), MeanAbsolutePercentageError() ]

trainer_module = BasicNnModule(generator(), batch_size=BATCH_SIZE, metrics=metrics)
plotter = MnistCganImageDataPlotter(output_dir=csv_logger.log_dir)

callback_list = [ EpochInferenceCallback(dataloader=data_module.train_dataloader(), data_plotter=plotter, num_samples=7) ]
trainer = Trainer(gpus=1, callbacks=callback_list, max_epochs=30, logger=[csv_logger], precision=32)
trainer.fit(trainer_module, data_module)
