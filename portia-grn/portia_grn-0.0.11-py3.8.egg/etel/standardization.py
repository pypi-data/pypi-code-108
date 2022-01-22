# -*- coding: utf-8 -*-
# standardization.py
# author: Antoine Passemiers

import numpy as np
import torch

from portia.etel.var_transformation import VariableTransformation


# torch.autograd.set_detect_anomaly(True)


class StandardizationTransform(VariableTransformation):

    def __init__(self, epsilon=1e-5):
        VariableTransformation.__init__(self)
        self.epsilon = epsilon

    def _forward(self, X):
        X = X - torch.mean(X, 0).unsqueeze(0)
        return X / (torch.std(X, 0, unbiased=True).unsqueeze(0) + self.epsilon)

    def log_jacobian(self, X):
        """
        n = X.size()[0]
        m = X.size()[1]

        mean = torch.mean(X, 0).unsqueeze(0)
        std = torch.std(X, 0, unbiased=True).unsqueeze(0) + 1e-10
        a = 1. / std
        u = X
        v = -(X - mean) / ((std ** 3) * (n - 1))
        uv = u * v
        d = a / (uv + 1e-10)
        log_det = torch.sum(torch.log(torch.abs(d)), 0)
        log_det += torch.log(torch.abs(1. + torch.sum(1. / d, 0)))
        log_det += torch.sum(torch.log(torch.abs(u * v)), 0)
        return torch.sum(log_det)
        """
        return 0
