# -*- coding: utf-8 -*-
# var_transformation.py
# author: Antoine Passemiers

from abc import ABCMeta, abstractmethod

import torch


class VariableTransformation(torch.nn.Module, metaclass=ABCMeta):

    def __init__(self):
        torch.nn.Module.__init__(self)

    def forward(self, X):
        Y = self._forward(X)
        log_jac = self.log_jacobian(X)
        return Y, log_jac

    @abstractmethod
    def _forward(self, X):
        pass

    @abstractmethod
    def log_jacobian(self, X):
        pass
