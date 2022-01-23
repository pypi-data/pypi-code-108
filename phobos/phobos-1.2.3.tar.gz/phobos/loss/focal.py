import torch
import logging

import torch.nn as nn


class FocalLoss(nn.Module):
    r"""Creates a criterion that measures the Focal Error
    between each element in the input :math:`X` and target :math:`Y`..

    Focal loss is computed as:

    .. math:: Loss(X,Y) = \alpha \cdot (1 - E_{BCE}(X,Y))^{\gamma} \cdot Loss_{BCE}(X,Y) , \gamma \geqslant 0

    where :math:`Loss_{BCE}(X,Y)` is the BCE Loss component, which is computed as:

    .. math::
        Loss_{BCE}(X,Y) = \sum\limits_{i=1}^N l(x_i,y_i), l(x_i,y_i) = - w_i \left[ y_i \cdot \log x_i + (1 - y_i) \cdot \log (1 - x_i) \right]

    where :math:`x_i \in X` and :math:`y_i \in Y` and :math:`E_{BCE} = exp( - Loss_{BCE}(X,Y))`

    Parameters
    ----------
    alpha : `float <https://docs.python.org/3/library/functions.html#float>`_
        alpha
    gamma : `int <https://docs.python.org/3/library/functions.html#int>`_
        gamma

    Examples
    --------
    >>> criterion = FocalLoss(alpha=1, gamma=2)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.ones(2, 1, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.0

    >>> criterion = FocalLoss(alpha=1, gamma=2)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 1, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    13.8155

    References
    ----------
    https://arxiv.org/pdf/1708.02002.pdf

    """

    def __init__(self, alpha, gamma):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma

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
            Focal loss computed between :attr:`predicted` and :attr:`target`.

        """
        logging.debug("Inside focal loss forward routine")
        predicted = predicted.float().squeeze()
        target = target.long()

        pt = torch.where(target == 1, predicted, 1 - predicted)
        F_loss = -1 * self.alpha * ((1 - pt) ** self.gamma) * torch.log(pt + 1e-6)
        return F_loss.mean()
