from typing import Any, Dict, List, Union
import torch
import torch.nn as nn
from pytorch_lightning import LightningModule
from torchmetrics.metric import Metric

class BoundaryEquilibriumGanModule(LightningModule):
    def __init__(
        self,
        generator_network: nn.Module = None,
        discriminator_network: nn.Module = None,
        optimizer_function: Any = torch.optim.Adam,
        optimizer_params: Dict = dict(lr=0.001, betas=(0.5, 0.9)),
        batch_size:int = 32,
        metrics: Union[List[Metric],Metric] = [],
    ):
        super().__init__()
        self.save_hyperparameters(ignore=["generator_network", "discriminator_network", "optimizer_function", "loss_function", "metrics"])

        self._net_g = generator_network
        self._net_d = discriminator_network
        self._optimizer_function = optimizer_function
        self._optimizer_params = optimizer_params

        self._batch_size = batch_size

        if isinstance(metrics, Metric):
            self._metrics = [metrics]
        elif isinstance(metrics, list):
            self._metrics = [m for m in metrics]

    def forward(self, input):
        return self._net_g(input)

    def on_pretrain_routine_start(self) -> None:
        self._is_cuda_enabled = self.device.type == 'cuda'

        for metric in self._metrics:
            metric = metric.to(self.device)
    
    def adversarial_loss(self, y_hat, y):
        return torch.mean(torch.abs(y_hat - y))

    def training_step(self, batch, batch_idx, optimizer_idx):
        # BEGAN hyper parameters
        gamma = 0.75
        lambda_k = 0.001
        k = 0.0

        i_real, o_real = batch

        # train generator
        if optimizer_idx == 0:

            # adversarial loss is binary cross-entropy
            o_fake = self(i_real)
            g_loss = self.adversarial_loss(self._net_d(i_real, o_fake), o_fake)
            self.log('train_loss', g_loss)
            loss = g_loss

        # train discriminator
        if optimizer_idx == 1:
            # Measure discriminator's ability to classify real from generated samples
            o_fake = self(i_real)

            real_loss = self.adversarial_loss(self._net_d(i_real,o_real), o_real)
            fake_loss = self.adversarial_loss(self._net_d(i_real,o_fake.detach()), o_fake.detach())

            # discriminator loss is the average of these
            d_loss = real_loss - k * fake_loss

            # ----------------
            # Update weights
            # ----------------
            diff = torch.mean(gamma * real_loss - fake_loss)
            # Update weight term for fake samples
            k = k + lambda_k * diff.item()
            k = min(max(k, 0), 1)  # Constraint to interval [0, 1]
            # Update convergence metric
            self.M = (d_loss + torch.abs(diff)).item()

            self.log('train_loss', d_loss)
            loss = d_loss

        return loss

    def configure_optimizers(self):
        self._net_g_optimizer = self._optimizer_function(self._net_g.parameters(), **self._optimizer_params)
        self._net_d_optimizer = self._optimizer_function(self._net_d.parameters(), **self._optimizer_params)
        return [ self._net_g_optimizer, self._net_d_optimizer ], []
    
    def _calculate_metrics(self, y, y_hat):
        result = {}
        for metric in self._metrics:
            result[metric.__class__.__name__] = metric(y_hat, y)
        return result
 