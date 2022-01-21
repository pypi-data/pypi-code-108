from typing import Any, Dict, List, Union

import torch
import torch.nn as nn
from torch.autograd import grad as torch_grad
import numpy
from pytorch_lightning import LightningModule
from torchmetrics.metric import Metric

class WassersteinGanGpModule(LightningModule):
    def __init__(
        self,
        generator_network: nn.Module = None,
        discriminator_network: nn.Module = None,
        optimizer_function: Any = torch.optim.Adam,
        optimizer_params: Dict = dict(lr=0.0001, betas=(0.5, 0.9)),
        batch_size:int = 32,
        metrics: Union[List[Metric],Metric] = [],
        critic_iterations: int = 5,
        lambda_gradient_penalty: int = 10
    ):
        super().__init__()
        self.save_hyperparameters(ignore=["generator_network", "discriminator_network", "optimizer_function", "loss_function", "metrics"])

        self._net_g = generator_network
        self._net_d = discriminator_network
        self._optimizer_function = optimizer_function
        self._optimizer_params = optimizer_params

        self._batch_size = batch_size
        self._lambda_gp = lambda_gradient_penalty
        self._critic_iterations = critic_iterations        

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

    def training_step(self, batch, batch_idx, optimizer_idx):
        i_real, o_real = batch
        
        if optimizer_idx == 0:
            o_fake = self(i_real)

            d_output = self._net_d(i_real, o_fake).squeeze()
            g_loss = -d_output.mean()
            loss = g_loss
            self.log('train_loss', loss)

        if optimizer_idx == 1:
            # Generate fake data
            o_fake = self(i_real)
            
            # Calculate probabilities on real and generated data
            d_real = self._net_d(i_real, o_real).squeeze()
            d_fake = self._net_d(i_real, o_fake).squeeze()
            
            # Get gradient penalty
            gradient_penalty, grad_norm = self._gradient_penalty(i_real, o_real, o_fake)

            # Create total loss and optimize
            d_loss = d_fake.mean() - d_real.mean() + (self._lambda_gp * gradient_penalty)
            loss = d_loss
            self.log('train_loss', loss)

        return loss
    
    def validation_step(self, batch, batch_idx):
        x_t, y_t = batch
        batch_size = x_t.shape[0]

        self._net_g.eval()
        y_f = self._net_g(x_t)
        self._net_g.train()

        y_f = y_f.squeeze()
        y_t = y_t.squeeze()
            
        for metric_name, metric_value in self._calculate_metrics(y_f, y_t).items():
            self.log(f'valid_{metric_name}', metric_value)

    def configure_optimizers(self):
        self._net_g_optimizer = self._optimizer_function(self._net_g.parameters(), **self._optimizer_params)
        self._net_d_optimizer = self._optimizer_function(self._net_d.parameters(), **self._optimizer_params)
        return (
            {'optimizer': self._net_g_optimizer, 'frequency': 1},
            {'optimizer': self._net_d_optimizer, 'frequency': self._critic_iterations}
        )
    
    def _calculate_metrics(self, y, y_hat):
        result = {}
        for metric in self._metrics:
            result[metric.__class__.__name__] = metric(y_hat, y)
        return result
 
    def _gradient_penalty(self, real_inputs, real_data, gen_data):
        batch_size = real_data.size()[0]
        dims = numpy.ones(len(real_data.shape), dtype=numpy.int64)
        dims[0] = batch_size
        dims = tuple(dims)
        t = torch.rand(dims, requires_grad=True, dtype=self.dtype, device=self.device)
        t = t.expand_as(real_data)
        
        t = t.cuda()

        # mixed sample from real and fake; make approx of the 'true' gradient norm
        interpol = t * real_data.data + (1-t) * gen_data.data

        interpol = interpol.cuda()

        #interpol = torch.tensor(interpol, requires_grad=True)
        
        prob_interpol = self._net_d(real_inputs, interpol)
        torch.autograd.set_detect_anomaly(True)
        gradients = torch_grad(outputs=prob_interpol, inputs=interpol, grad_outputs=torch.ones(prob_interpol.size(), device=self.device), create_graph=True, retain_graph=True)[0]
        gradients = gradients.view(batch_size, -1)
        #grad_norm = torch.norm(gradients, dim=1).mean()
        #self.losses['gradient_norm'].append(grad_norm.item())

        # add epsilon for stability
        eps = 1e-10
        gradients_norm = torch.sqrt(torch.sum(gradients**2, dim=1, dtype=torch.double) + eps)
        #gradients = gradients.cpu()
        # comment: precision is lower than grad_norm (think that is double) and gradients_norm is float
        return (torch.max(torch.zeros(1, dtype=torch.double, device=self.device), gradients_norm.mean() - 1) ** 2), gradients_norm.mean().item()
