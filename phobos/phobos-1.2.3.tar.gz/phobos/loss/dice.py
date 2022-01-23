import torch
import logging

import torch.nn as nn


class DiceLoss(nn.Module):
    r"""Creates a criterion that measures and maximizes Dice Error
    between each element in the input :math:`X` and target :math:`Y`.

    Dice Cofficient between inputs :math:`X` and :math:`Y` is computed as:

    .. math:: DC(X,Y) = \frac{2 \cdot | X \cap Y | + \epsilon }{|X| + |Y| + \epsilon}

    where :math:`\epsilon` is a constant added for numerical stability.

    Dice Loss is computed as:

    .. math:: Loss_{DC}(X,Y) = 1 - DC(X,Y)

    Please note that Dice Loss computed finally will be negated as our
    intention is to maximize Dice Loss. General PyTorch optimizers can be
    employed to minimize Dice Loss.

    Parameters
    ----------
    eps : `float <https://docs.python.org/3/library/functions.html#float>`_
        epsilon

    Examples
    --------
    >>> criterion = DiceLoss()
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.ones(2, 1, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.0

    >>> criterion = DiceLoss()
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 1, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    1.0

    References
    ----------
    https://www.kaggle.com/bigironsphere/loss-function-library-keras-pytorch

    """

    def __init__(self, eps=1e-7):
        super(DiceLoss, self).__init__()
        self.eps = eps

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
            Dice loss computed between :attr:`predicted` and :attr:`target`.

        """
        logging.debug("Inside dice loss forward routine")
        predicted = predicted.float().view(-1)
        target = target.long().view(-1)

        intersection = torch.sum(target * predicted)

        target_o = torch.sum(target)
        predicted_o = torch.sum(predicted)

        denominator = target_o + predicted_o

        dice_loss = 1.0 - (2.0 * intersection + self.eps) /\
                          (denominator + self.eps)

        return dice_loss.mean()
