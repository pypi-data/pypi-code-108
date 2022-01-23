import torch
import logging

import torch.nn as nn
from torch.nn import functional as F


class MLDiceLoss(nn.Module):
    r"""Creates a criterion that measures and maximizes Dice Error
    between each element in the input :math:`X` and target :math:`Y`.

    Dice Cofficient between inputs :math:`X` and :math:`Y` is computed as:

    .. math:: DC(X_{c},Y_{c}) = \frac{2 \cdot | X_{c} \circ Y_{c} |}{|X_{c}| + |Y_{c}| + \epsilon}

    where :math:`\epsilon` is a constant added for numerical stability and `c` is the channel index.

    Dice Loss is computed as:

    .. math:: Loss_{DC}(X,Y) = \sum_{c} - w_{c} \cdot DC(X_{c},Y_{c})

    where,

    .. math:: w_{c} = \frac{e^{|Y_{c}|}}{\sum_{\hat{c}}e^{|Y_{\hat{c}}|}}

    Please note that Dice Loss computed finally will be negated as our
    intention is to maximize Dice Loss. General PyTorch optimizers can be
    employed to minimize Dice Loss.

    Parameters
    ----------
    eps : `float <https://docs.python.org/3/library/functions.html#float>`_
        epsilon

    Examples
    --------
    >>> criterion = MLDiceLoss()
    >>> predicted = torch.ones(2, 5, 32, 32)
    >>> target = torch.ones(2, 5, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    -1.0

    >>> criterion = MLDiceLoss()
    >>> predicted = torch.ones(2, 5, 32, 32)
    >>> target = torch.zeros(2, 5, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.0
    
    References
    ----------
    https://www.kaggle.com/bigironsphere/loss-function-library-keras-pytorch

    """

    def __init__(self, eps=1e-7):
        """Initialise loss module.

        Parameters
        ----------
        eps : `float <https://docs.python.org/3/library/functions.html#float>`_
            epsilon

        """
        super(MLDiceLoss, self).__init__()
        self.eps = eps

    def forward(self, predicted, target, dim=(2, 3)):
        """Compute loss between :attr:`predicted` and :attr:`target`.

        :attr:`predicted` and :attr:`target` are tensors of shape :math:`[B,C,H,W]`

        Parameters
        ----------
        predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Predicted output tensor from a model.
        target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Ground truth tensor.

        Returns
        -------
        `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            MultiLabel Dice loss computed between :attr:`predicted` and :attr:`target`.

        """
        logging.debug("Inside dice loss forward routine")
        predicted = predicted.float()
        target = target.float()

        intersection = torch.sum(target * predicted, dim=dim)

        target_o = torch.sum(target, dim=dim)
        predicted_o = torch.sum(predicted, dim=dim)

        denominator = target_o + predicted_o 

        dice_loss = (2.0 * intersection) /(denominator + self.eps)

        w = F.softmax(target_o, dim=1)

        ml_dice_loss = torch.sum(dice_loss*w, dim=1)

        return -1*ml_dice_loss.mean()
