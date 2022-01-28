import os
import torch
import torch.nn as nn

from torch.autograd import Function
from torch import optim
from torch.optim.optimizer import Optimizer
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

import numpy as np
from numpy import linalg
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

class FinancialDataset(Dataset):
    def __init__(self, X):
        self.device = 'cpu'

        self.dataset = torch.from_numpy(X).type(torch.float)
        x, y = np.linspace(0, 1, X.shape[0]), X.sum(axis=1) 
        bias = np.ones_like(x)
        XX = np.c_[bias, x]
        b = linalg.inv(XX.T@XX) @ XX.T @ y
        self.target = torch.from_numpy(XX@b).type(torch.float)
        
        self.train_dataset = self.dataset
        self.test_dataset = self.train_dataset
        

    def __len__(self):
        if self.mode == 'train':
            return self.train_dataset.size()[0]
        elif self.mode == 'test':
            return self.test_dataset.size()[0]

    def __getitem__(self, idx):
        if self.mode == 'train':
            x_item = self.train_dataset[idx, :].squeeze().to(self.device)
            y_item = self.target[idx].squeeze().to(self.device)
        elif self.mode == 'test':
            x_item = self.test_dataset[idx, :].squeeze().to(self.device)
            y_item = self.target[idx].squeeze().to(self.device)
        else : pass
        return x_item, y_item

    def type(self, mode='train'):
        self.mode = mode
        return self
    

class Adamax(Optimizer):
    """Implements Adamax algorithm (a variant of Adam based on infinity norm).

    It has been proposed in `Adam: A Method for Stochastic Optimization`__.

    Args:
        params (iterable): iterable of parameters to optimize or dicts defining
            parameter groups
        lr (float, optional): learning rate (default: 2e-3)
        betas (Tuple[float, float], optional): coefficients used for computing
            running averages of gradient and its square
        eps (float, optional): term added to the denominator to improve
            numerical stability (default: 1e-8)
        weight_decay (float, optional): weight decay (L2 penalty) (default: 0)

    __ https://arxiv.org/abs/1412.6980
    """

    def __init__(self, params, lr=2e-3, betas=(0.9, 0.999), eps=1e-8,
                 weight_decay=0):
        if not 0.0 <= lr:
            raise ValueError("Invalid learning rate: {}".format(lr))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {}".format(eps))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter at index 0: {}".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter at index 1: {}".format(betas[1]))
        if not 0.0 <= weight_decay:
            raise ValueError("Invalid weight_decay value: {}".format(weight_decay))

        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        super(Adamax, self).__init__(params, defaults)

    @staticmethod
    def adamax(params,
               grads,
               exp_avgs,
               exp_infs,
               state_steps,
               *,
               eps: float,
               beta1: float,
               beta2: float,
               lr: float,
               weight_decay: float):
        r"""Functional API that performs adamax algorithm computation.

        See :class:`~torch.optim.Adamax` for details.
        """

        for i, param in enumerate(params):
            grad = grads[i]
            exp_avg = exp_avgs[i]
            exp_inf = exp_infs[i]
            step = state_steps[i]

            if weight_decay != 0:
                grad = grad.add(param, alpha=weight_decay)

            # Update biased first moment estimate.
            exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
            # Update the exponentially weighted infinity norm.
            norm_buf = torch.cat([
                exp_inf.mul_(beta2).unsqueeze(0),
                grad.abs().add_(eps).unsqueeze_(0)
            ], 0)
            torch.amax(norm_buf, 0, keepdim=False, out=exp_inf)

            bias_correction = 1 - beta1 ** step
            clr = lr / bias_correction

            param.addcdiv_(exp_avg, exp_inf, value=-clr)     
            
    @torch.no_grad()
    def step(self, closure=None):
        """Performs a single optimization step.

        Args:
            closure (callable, optional): A closure that reevaluates the model
                and returns the loss.
        """
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            params_with_grad = []
            grads = []
            exp_avgs = []
            exp_infs = []
            state_steps = []

            beta1, beta2 = group['betas']
            eps = group['eps']
            lr = group['lr']
            weight_decay = group['weight_decay']

            for p in group['params']:
                if p.grad is None:
                    continue
                params_with_grad.append(p)
                if p.grad.is_sparse:
                    raise RuntimeError('Adamax does not support sparse gradients')
                grads.append(p.grad)

                state = self.state[p]

                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['exp_inf'] = torch.zeros_like(p, memory_format=torch.preserve_format)

                exp_avgs.append(state['exp_avg'])
                exp_infs.append(state['exp_inf'])

                state['step'] += 1
                state_steps.append(state['step'])
                
            self.adamax(params_with_grad,
                     grads,
                     exp_avgs,
                     exp_infs,
                     state_steps,
                     eps=eps,
                     beta1=beta1,
                     beta2=beta2,
                     lr=lr,
                     weight_decay=weight_decay)

        return loss                

    
class WeightBuffer(Function):
    @staticmethod
    def forward(ctx, params):
        ctx.save_for_backward(params)
        return params

    @staticmethod
    def backward(ctx, grad_output):
        params, = ctx.saved_tensors
        buffer = torch.where(params < 0, -1, 1)
        grad_output = torch.where(grad_output.clone() <0, 0, 0)
        return grad_output * buffer * 0

    
class Model(nn.Module):
    def __init__(self, X):
        super(Model, self).__init__()
        self.linear1 = nn.Linear(X.shape[1], 1, bias=False)
        nn.init.ones_(self.linear1.weight)

    def forward(self, x):
        x = self.linear1(x.type(torch.float))
        return x    
 

class Criterion(nn.Module):
    def __init__(self):
        super(Criterion, self).__init__()
        self.mse = nn.MSELoss()

    def forward(self, hypothesis, target, model):
        loss = (hypothesis-target)**2
        l2_lambda = 10
        l2_reg = torch.tensor(0.)
        for param in model.parameters():
            l2_reg += torch.norm(param)
        loss += l2_lambda * l2_reg
        return loss.sum()


def SetupInstances(X):
    dataset = FinancialDataset(X=X)
    train_dataloader = DataLoader(dataset.type('train'), batch_size=10, shuffle=True, drop_last=False)
    test_dataloader = DataLoader(dataset.type('test'), batch_size=10, shuffle=True, drop_last=False)

    model = Model(X)
    criterion = Criterion()
    optimizer = Adamax(model.parameters(), lr=0.01)
    return train_dataloader, test_dataloader, model, criterion, optimizer


def Train(train_dataloader, test_dataloader, model, criterion, optimizer, verbose=False, epochs=500):
    for epoch in tqdm(range(epochs)):
        losses = []
        model.train()
        for batch_idx, (x_train, y_train) in enumerate(train_dataloader):
            # Forward
            hypothesis = model(x_train.squeeze())
            cost = criterion(hypothesis.squeeze(), y_train.squeeze(), model)
            
            # Backward
            optimizer.zero_grad()
            cost.backward()
            optimizer.step()
            for param in model.parameters():
                param.data.clamp_(0)

            losses.append(cost)
            
        # Alert
        if verbose:
            if epoch%10 == 0:
                print(model.linear1.weight)
                print(f'[Training][{epoch+1}/{epochs}] : ', float(sum(losses).data))

    return model.linear1.weight

