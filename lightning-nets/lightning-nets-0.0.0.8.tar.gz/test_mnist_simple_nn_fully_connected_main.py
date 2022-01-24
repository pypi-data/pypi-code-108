import os
import setuptools

import numpy as np
from pytorch_lightning import Trainer

import torch
import torch.nn as nn


import pytorch_lightning.loggers as pl_loggers

from lightning_nets.data import *
from lightning_nets.hooks import *
from lightning_nets.modules import BasicNnModule
from lightning_nets.hooks.plotters import *

from torchmetrics import *

AVAIL_GPUS = min(1, torch.cuda.device_count())
PATH_DATASETS = os.environ.get("PATH_DATASETS", ".")
BATCH_SIZE = 64

class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.label_emb = nn.Embedding(10, 10)
        
        self.model = nn.Sequential(
            nn.Linear(10, 256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(256, 512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(512, 1024),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(1024, 784),
            nn.Tanh()
        )

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

    def forward(self, labels):
        labels = labels.long()
        c = self.label_emb(labels)
        out = self.model(c)
        return out.view(labels.size(0), 28, 28)

csv_logger = pl_loggers.CSVLogger(save_dir=os.getcwd(), name="logs", flush_logs_every_n_steps=3)

data_module = MNISTDataModule(batch_size=BATCH_SIZE)

metrics = [ MeanSquaredError(), MeanSquaredError(squared=False), MeanAbsoluteError(), MeanAbsolutePercentageError() ]

trainer_module = BasicNnModule(Generator(), batch_size=BATCH_SIZE, metrics=metrics)
plotter = MnistCganImageDataPlotter(output_dir=csv_logger.log_dir)

callback_list = [ EpochInferenceCallback(dataloader=data_module.train_dataloader(), data_plotter=plotter, num_samples=7) ]
trainer = Trainer(gpus=1, callbacks=callback_list, max_epochs=30, logger=[csv_logger], precision=32)
trainer.fit(trainer_module, data_module)