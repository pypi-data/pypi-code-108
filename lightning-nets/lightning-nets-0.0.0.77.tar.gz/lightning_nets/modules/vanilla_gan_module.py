from logging import logProcesses
from typing import Any, Dict, List, Union

import torch
import torch.nn as nn

from pytorch_lightning import LightningModule
from torchmetrics.metric import Metric

class VanillaGanModule(LightningModule):
    def __init__(
        self,
        generator_network: nn.Module = None,
        discriminator_network: nn.Module = None,
        optimizer_function: Any = torch.optim.Adam,
        optimizer_params: Dict = dict(lr=0.0005, betas=(0.5, 0.9)),
        loss_function: Any = nn.BCELoss(),
        batch_size:int = 32,
        metrics: Union[List[Metric],Metric] = []
    ):
        super().__init__()
        self.save_hyperparameters(ignore=["generator_network", "discriminator_network", "optimizer_function", "loss_function", "metrics"])

        self._net_g = generator_network
        self._net_d = discriminator_network
        self._optimizer_function = optimizer_function
        self._optimizer_params = optimizer_params

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
    
    def generator_step(self, x, y):
        """
        Training step for generator
        1. Sample random noise
        2. Pass noise to generator to
        generate images
        3. Classify generated images using
        the discriminator
        4. Backprop loss
        """
        # Generate images
        generated_imgs = self(x)#z)

        # Classify generated images
        # using the discriminator
        d_output = torch.squeeze(self._net_d(x, generated_imgs))

        # Backprop loss
        g_loss = self._loss_function(d_output, torch.ones(x.shape[0], device=self.device))

        return g_loss

    def discriminator_step(self, x, y):
        """
        Training step for discriminator
        1. Get actual images
        2. Get fake images from generator
        3. Predict probabilities of actual images
        4. Predict probabilities of fake images
        5. Get loss of both and backprop
        """
        # Real images
        d_output = torch.squeeze(self._net_d(x, y))
        loss_real = nn.BCELoss()(d_output, torch.ones(x.shape[0], device=self.device))

        # Fake images
        generated_imgs = self(x)
        d_output = torch.squeeze(self._net_d(x, generated_imgs))
        loss_fake = self._loss_function(d_output, torch.zeros(x.shape[0], device=self.device))

        return loss_real + loss_fake
  
    def training_step(self, batch, batch_idx, optimizer_idx):
        i_real, o_real = batch
        
        real = torch.ones(o_real.shape[0]).to(device=self.device, dtype=self.dtype)
        fake = torch.zeros(o_real.shape[0]).to(device=self.device, dtype=self.dtype)

        if optimizer_idx == 0:
            o_fake = self(i_real)

            d_output = self._net_d(i_real, o_fake).squeeze()

            loss = self._loss_function(d_output, real)
            self.log('train_loss', loss)

        if optimizer_idx == 1:
            d_output = torch.squeeze(self._net_d(i_real, o_real))
            loss_real = self._loss_function(d_output, real)# torch.ones(x.shape[0], device=self.device))

            generated_imgs = self(i_real)
            d_output = self._net_d(i_real, generated_imgs).squeeze()
            loss_fake = self._loss_function(d_output, fake)

            loss = (loss_real + loss_fake) / 2
            self.log('train_loss', loss)

        return loss
    
    def validation_step(self, batch, batch_idx):
        x_t, y_t = batch

        self.eval()
        y_f = self(x_t)
        self.train()
        
        y_f = y_f.squeeze()
        y_t = y_t.squeeze()
        
        for metric_name, metric_value in self._calculate_metrics(y_f, y_t).items():
            self.log(f'valid_{metric_name}', metric_value)

    def configure_optimizers(self):
        self._net_g_optimizer = self._optimizer_function(self._net_g.parameters(), **self._optimizer_params)
        self._net_d_optimizer = self._optimizer_function(self._net_d.parameters(), **self._optimizer_params)
        return [self._net_g_optimizer, self._net_d_optimizer], []
    
    def _calculate_metrics(self, y, y_hat):
        result = {}
        for metric in self._metrics:
            result[metric.__class__.__name__] = metric(y_hat, y)
        return result