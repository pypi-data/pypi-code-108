from typing import Any, Dict, List, Union

import torch
from torch.functional import Tensor
import torch.nn as nn

from pytorch_lightning import LightningModule
from torchmetrics.metric import Metric

class BasicNnModule(LightningModule):
    def __init__(
        self,
        neural_network: nn.Module = None,
        optimizer_function: Any = torch.optim.Adam,
        optimizer_params: Dict = dict(lr=0.0001, betas=(0.5, 0.9)), 
        loss_function: Any = nn.MSELoss(),
        batch_size:int = 32,
        metrics: Union[List[Metric],Metric] = []
        ):
        super().__init__()
        self.save_hyperparameters(ignore=["neural_network", "optimizer_function", "loss_function", "metrics"])

        self._net_g = neural_network
        self._net_g_optimizer = optimizer_function(self._net_g.parameters(), **optimizer_params)
        self._loss_function = loss_function
        self._batch_size = batch_size
        
        if isinstance(metrics, Metric):
            self._metrics = [metrics]
        elif isinstance(metrics, list):
            self._metrics = [m for m in metrics]
          
    def forward(self, input):
        return self._net_g(input)

    def on_pretrain_routine_start(self) -> None:
        for metric in self._metrics:
            metric = metric.to(self.device)
        return super().on_pretrain_routine_start()

    def training_step(self, batch, batch_idx):
        x_t, y_t = batch
        y_f = self(x_t)
        loss = self._loss_function(y_f, y_t)

        self.log('train_loss', loss)
        return loss

    def validation_step(self, batch, batch_idx):
        x_t, y_t = batch

        self.eval()
        y_f = self(x_t)
        self.train()

        y_f = y_f.squeeze()
        y_t = y_t.squeeze()

        loss = self._loss_function(y_f, y_t)
        
        self.log('valid_loss', loss)
        for metric_name, metric_value in self._calculate_metrics(y_f, y_t).items():
            self.log(f'valid_{metric_name}', metric_value)
        return loss

    def configure_optimizers(self):
        return self._net_g_optimizer
    
    def _calculate_metrics(self, y, y_hat):
        result = {}
        for metric in self._metrics:
            m = metric(y_hat, y)
            if isinstance(m, Tensor) and m.requires_grad:
                m = m.detach()
            result[metric.__class__.__name__] = m
        return result