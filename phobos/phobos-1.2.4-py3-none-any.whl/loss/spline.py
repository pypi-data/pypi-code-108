import torch
import logging

import torch.nn as nn


class SplineLoss(nn.Module):
    r"""Creates a criterion that measures the Active Contour Error or Spline Error
    between predicted input :math:`U` and ground truth input :math:`V`.

    For :math:`X , Y \in \left[ 0 , 1 \right]^{m \times n}`, where :math:`m` and :math:`n` are the input dimensions,

    Active Contour Loss or Spline Loss is computed as:

    .. math:: Loss_{AC} = Length + \lambda \cdot Region

    in which,

    .. math:: Length = \int_C \left| \nabla X \right| ds

    .. math:: Region = \int_{\Omega} ((1-Y)^{2} - Y^{2})Xdu

    :math:`Length` and :math:`Region` can be written in pixel wise form as:

    .. math:: Length = \sum\limits_{\Omega}^{i=1,j=1} \sqrt{\left| (\nabla X_{u_{i,j}})^{2} + (\nabla X_{v_{i,j}})^{2}\right| + \epsilon }

    where :math:`u` and :math:`v` from :math:`X_{u_{i,j}}` and :math:`X_{v_{i,j}}` are horizontal and vertical directions respectively,

    and :math:`\epsilon` is a constant added for numerical stability.

    .. math:: Region = \left| \sum\limits_{\Omega}^{i=1,j=1} X_{i,j} \cdot (1-Y_{i,j})^{2}\right| + \left| \sum\limits_{\Omega}^{i=1,j=1} (1-X_{i,j}) \cdot Y_{i,j}^{2}\right|

    Parameters
    ----------
    patch_size : `int <https://docs.python.org/3/library/functions.html#int>`_
        patch size
    w : `int <https://docs.python.org/3/library/functions.html#int>`_
        weight
    lambda_p : `int <https://docs.python.org/3/library/functions.html#int>`_
        lambda

    Examples
    --------
    >>> criterion = SplineLoss(w=1, lambda_p=1, patch_size=32)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.ones(2, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.0

    >>> criterion = SplineLoss(w=1, lambda_p=1, patch_size=32)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()    
    2.0

    References
    ----------
    https://sci-hub.do/https://ieeexplore.ieee.org/document/8953484
    """

    def __init__(self, patch_size, w=1, lambda_p=1):
        super(SplineLoss, self).__init__()
        self.patch_size = patch_size
        self.w = w
        self.lambda_p = lambda_p
        self.epsilon = 1e-8

    def forward(self, predicted, target):
        """Compute loss between :attr:`predicted` and :attr:`target`.

        :attr:`predicted` and :attr:`target` are tensors of shape :math:`[B,1,H,W]`

        Parameters
        ----------
        predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Predicted output tensor from a model.
        target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Ground truth tensor.

        Returns
        -------
        `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Spline loss computed between :attr:`predicted` and :attr:`target`.

        """
        logging.debug("Inside spline loss forward routine")
        predicted = predicted.float()
        target = target.float()

        # horizontal and vertical directions
        x = predicted[:, 1:, :] - predicted[:, :-1, :]
        y = predicted[:, :, 1:] - predicted[:, :, :-1]

        delta_x = x[:, 1:, :-2]**2
        delta_y = y[:, :-2, 1:]**2
        delta_u = torch.abs(delta_x + delta_y)

        # where is a parameter to avoid square root is zero in practice.
        epsilon = self.epsilon
        # equ.(11) in the paper
        length = self.w * torch.sum(torch.sqrt(delta_u + epsilon))

        c_1 = torch.ones((self.patch_size, self.patch_size))
        c_2 = torch.zeros((self.patch_size, self.patch_size))

        c_1 = c_1.to(predicted.device)
        c_2 = c_2.to(predicted.device)

        region_in = torch.abs(
            torch.sum(
                predicted[:, :, :] * ((target[:, :, :] - c_1)**2)))  # equ.(12) in the paper
        region_out = torch.abs(
            torch.sum(
                (1 - predicted[:, :, :]) * ((target[:, :, :] - c_2) ** 2)))  # equ.(12) in the paper

        loss = length + self.lambda_p * (region_in + region_out)

        return loss / target.nelement()
