import torch
import torch.nn as nn
import logging


class BCEJaccardLoss(nn.Module):
    r"""Creates a criterion that measures the BCE Jaccard Error
    between each element in the input :math:`X` and target :math:`Y`.

    Final loss is computed as a weighted average between BCE Loss and Jaccard Loss:

    .. math:: Loss(X,Y) = (1 - w_j) \cdot Loss_{BCE}(X,Y) + w_j \cdot Loss_{Jaccard}(X,Y)

    where :math:`w_j` is Jaccard Weight

    :math:`Loss_{BCE}(X,Y)` is the BCE Loss component, which is computed as:

    .. math::
        Loss_{BCE}(X,Y) = \sum\limits_{i=1}^N l(x_i,y_i), l(x_i,y_i) = - w_i \left[ y_i \cdot \log x_i + (1 - y_i) \cdot \log (1 - x_i) \right]

    where :math:`x_i \in X` and :math:`y_i \in Y`

    :math:`Loss_{Jaccard}(X,Y)` is the Jaccard Loss component, which is computed as:

    .. math::
        Loss_{Jaccard}(X,Y) = \frac{| X \cap Y | + \epsilon }{| X \cup Y | + \epsilon } = \frac{| X \cap Y | + \epsilon }{|X| + |Y| - | X \cap Y | + \epsilon }

    where :math:`\epsilon` is a constant added for numerical stability

    Parameters
    ----------
    jaccard_weight : `float <https://docs.python.org/3/library/functions.html#float>`_
        jaccard weight
    eps : `float <https://docs.python.org/3/library/functions.html#float>`_
        epsilon

    Examples
    --------
    >>> criterion = BCEJaccardLoss(jaccard_weight=0.5)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.ones(2, 1, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    0.1344

    >>> criterion = BCEJaccardLoss(jaccard_weight=0.5)
    >>> predicted = torch.ones(2, 1, 32, 32)
    >>> target = torch.zeros(2, 1, 32, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    50.5

    References
    ----------
    https://pytorch.org/docs/stable/generated/torch.nn.BCELoss.html

    https://www.kaggle.com/bigironsphere/loss-function-library-keras-pytorch

    """

    def __init__(self, jaccard_weight, eps=1e-15):
        super(BCEJaccardLoss, self).__init__()
        self.eps = eps
        self.jaccard_weight = jaccard_weight

        self.nll_loss = nn.BCELoss()

        self._stash_bce_loss = 0
        self._stash_jaccard = 0

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
            BCEJaccard loss computed between :attr:`predicted` and
            :attr:`target`.

        """
        logging.debug("Inside binary_jaccard loss forward routine")
        predicted = predicted.float()
        target = target.float()

        self._stash_bce_loss = self.nll_loss(predicted, target)
        loss = (1 - self.jaccard_weight) * self._stash_bce_loss

        jaccard_target = (target == 1).float()
        jaccard_output = torch.sigmoid(predicted)

        intersection = (jaccard_output * jaccard_target).sum()
        union = jaccard_output.sum() + jaccard_target.sum()

        jaccard_score = (
            (intersection + self.eps) / (union - intersection + self.eps))
        self._stash_jaccard = jaccard_score
        loss += self.jaccard_weight * (1. - jaccard_score)

        return loss
