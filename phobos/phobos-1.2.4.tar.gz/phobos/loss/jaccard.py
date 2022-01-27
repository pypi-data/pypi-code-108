import torch
import logging

import torch.nn as nn


class JaccardLoss(nn.Module):
    r"""Creates a criterion that measures the Jaccard Error
    between each element in the input :math:`X` and target :math:`Y`.

    Jaccard Loss is computed as:

    .. math::
        Loss(X,Y) = \frac{| X \cap Y | + \epsilon }{| X \cup Y | + \epsilon } = \frac{| X \cap Y | + \epsilon }{|X| + |Y| - | X \cap Y | + \epsilon }

    where :math:`\epsilon` is a constant added for numerical stability

    Parameters
    ----------
    eps : `float <https://docs.python.org/3/library/functions.html#float>`_
        epsilon

    Examples
    --------
    >>> criterion = JaccardLoss()
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.5

    >>> criterion = JaccardLoss()
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.5

    References
    ----------
    https://www.kaggle.com/bigironsphere/loss-function-library-keras-pytorch

    """

    def __init__(self, eps=1e-7):
        super(JaccardLoss, self).__init__()
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
            Jaccard loss computed between :attr:`predicted` and :attr:`target`.

        """
        logging.debug("Inside jaccard loss forward routine")
        predicted = predicted.float()
        target = target.long()

        num_classes = predicted.shape[1]
        if num_classes == 1:
            target_1_hot = torch.eye(num_classes + 1)[target.squeeze(1)]
            target_1_hot = target_1_hot.permute(0, 3, 1, 2).float()
            target_1_hot_f = target_1_hot[:, 0:1, :, :]
            target_1_hot_s = target_1_hot[:, 1:2, :, :]
            target_1_hot = torch.cat([target_1_hot_s, target_1_hot_f], dim=1)
            # pos_prob = torch.sigmoid(predicted) #apply before model output
            # neg_prob = 1 - predicted
            # probas = torch.cat([predicted, neg_prob], dim=1)
        else:
            target_1_hot = torch.eye(num_classes)[target.squeeze(1)]
            target_1_hot = target_1_hot.permute(0, 3, 1, 2).float()
            # probas = F.softmax(predicted, dim=1) #apply before model output

        target_1_hot = target_1_hot.to(predicted.device)

        target_1_hot = target_1_hot.type(predicted.type())
        dims = (0,) + tuple(range(2, target.ndimension()))
        intersection = torch.sum(predicted * target_1_hot, dims)
        cardinality = torch.sum(predicted + target_1_hot, dims)
        union = cardinality - intersection
        jacc_loss = (intersection / (union + self.eps)).mean()
        return (1 - jacc_loss)
