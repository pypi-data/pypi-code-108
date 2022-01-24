import os
import setuptools

from torch.utils.data import DataLoader

import numpy as np
from pytorch_lightning import LightningModule, Trainer

import torch
import torch.nn as nn

import torchmetrics

import pytorch_lightning.loggers as pl_loggers
import pytorch_lightning.callbacks as pl_callbacks

from lightning_nets.data import *
from lightning_nets.hooks import *
from lightning_nets.modules import *

class EpochInferenceCallback(pl_callbacks.Callback):
    def __init__(self, dataloader:DataLoader, data_plotter:DataPlotter = None, num_samples:int = 5, shuffle:bool = True) -> None:
        super().__init__()
        self.data_plotter = data_plotter
        
        data_loader = DataLoader(dataset=dataloader.dataset, batch_size=num_samples, shuffle=shuffle)
        _, sample = enumerate(data_loader).__next__()

        self.x, self.y = sample

        self.data_loader = DataLoader(PredictTorchDataset(self.x))
        self._current_epoch = 0
        self._global_step = 0

    def on_epoch_end(self, trainer: Trainer, pl_module: LightningModule) -> None:
        if self._current_epoch == trainer.current_epoch:
            return
        
        self._current_epoch = trainer.current_epoch
        self._global_step = trainer.global_step

        x = self.to_tensor(self.x, pl_module, self.x.dtype)
        y = self.to_tensor(self.y, pl_module, self.y.dtype)

        pl_module.eval()
        y_hat = pl_module(x)
        pl_module.train()

        x = self.to_numpy(x, pl_module)
        y = self.to_numpy(y, pl_module)
        y_hat = self.to_numpy(y_hat, pl_module)

        if self.data_plotter is not None:
            self.data_plotter.plot_data(x, y, y_hat, current_epoch=self._current_epoch, global_step=self._global_step)
        return

    def to_tensor(self, data: Any, pl_module: LightningModule, dtype: torch.dtype=torch.float32):
        """
        A utility method for converting data to tensor objects 

        Args:
            data (Any): The data to convert to a tensor
            dtype (torch.dtype, optional): Defaults to torch.float32.

        Raises:
            TypeError: If data is not a list, or not convertible to a numpy ndarray.

        Returns:
            torch.Tensor: A tensor
        """
        if isinstance(data, list):
            result = torch.tensor(np.asarray(data), dtype=dtype).to(device=pl_module.device)
        elif isinstance(data, np.ndarray):
            result = torch.tensor(data, dtype=dtype).to(device=pl_module.device)
        elif isinstance(data, torch.Tensor):
            result = data.clone().detach().requires_grad_(data.requires_grad).to(device=pl_module.device, dtype=dtype)
        else:
            raise TypeError("type {} of data is not acceptable".format(type(data)))
        return result

    def to_numpy(self, data: torch.Tensor, pl_module: LightningModule):
        """
        Converts a torch.Tensor to a numpy.ndarray

        Args:
            data (torch.Tensor): The array to convert

        Returns:
            numpy.ndarray: The converted array
        """
        if data.requires_grad:
            data = data.detach()
        if pl_module.device != torch.device("cpu"):
            data = data.cpu()
        return data.numpy()
