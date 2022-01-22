# -*- coding: utf-8 -*-
# box_cox.py
# author: Antoine Passemiers

import numpy as np
import torch
from sklearn.preprocessing import PowerTransformer

from portia.etel.var_transformation import VariableTransformation


class BoxCoxTransform(VariableTransformation):
    """Differentiable Box-Cox transform.

    Attributes:
        n_variables (int): Number of genes.
        bc_lambda_1 (:obj:`torch.nn.Parameter`): Vector of Box-Cox parameters, where i-th
            component corresponds to the parameter of the transform
            associated to gene i.
        _mu (:obj:`torch.nn.Parameter`): Mean vector, where i-th component is the average
            expression of gene i.
        _mu (:obj:`torch.nn.Parameter`): Standard deviation vector, where i-th component is the
            standard deviation of gene i.
    """

    def __init__(self, n_variables):
        VariableTransformation.__init__(self)
        self.n_variables = n_variables
        self.bc_lambda_1 = torch.nn.Parameter(torch.ones(1, self.n_variables))

        self._mu = None
        self._std = None
        self.sum_log_x = None

    def init(self, X_arr):
        """Initializes Box-Cox parameters.

        Each transform is fitted based on the marginal likelihood associated
        to one gene, instead of the joint likelihood.

        Args:
            X_arr (:obj:`np.ndarray`): NumPy array containing the input data.
        """
        transformer = PowerTransformer(method='box-cox', standardize=False)
        transformer.fit_transform(X_arr)
        self.bc_lambda_1.data = torch.FloatTensor(transformer.lambdas_.reshape(1, self.n_variables))
        self._mu = torch.FloatTensor(np.mean(X_arr, axis=0)).unsqueeze(0)
        self._std = torch.FloatTensor(np.std(X_arr, axis=0)).unsqueeze(0)
        self.sum_log_x = torch.sum(torch.log(torch.FloatTensor(X_arr)), dim=0)

    def _forward(self, X):
        Y1 = ((X ** self.bc_lambda_1) - 1.) / self.bc_lambda_1
        Y2 = torch.log(X)
        return torch.where(self.bc_lambda_1 != 0, Y1, Y2)

    def log_jacobian(self, X):
        return torch.sum((self.bc_lambda_1 - 1.) * self.sum_log_x)
