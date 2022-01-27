import torch.nn as nn


class MAELoss(nn.Module):
    r"""Creates a criterion that minimizes Mean Absolute Error (with mask support) between the input :math:`X` and target :math:`Y`.

    Mean Squared Error between inputs :math:`X` and :math:`Y` with mask :math:`M` is computed as:

    .. math:: MAE(X,Y) = \frac{1}{n} \sum\limits_{i}^{n} | (X_i - Y_i) \cdot M_i |

    where :math: mask `M` is binary tensor.

    reduction='mean', If args.mask=True masked version will be used.

    If args.mask=False :math:`M`=torch.ones_like(:math:`X`).

    Examples
    --------
    >>> criterion = MAELoss(mask=False)
    >>> predicted = torch.ones(2, 32)
    >>> target = torch.zeros(2, 32)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    1.0

    >>> mask = torch.zeros((2,32), dtype=torch.float32)
    >>> criterion = MAELoss(mask=True)
    >>> predicted = torch.ones(2, 32)
    >>> target = torch.zeros(2, 32)
    >>> loss = criterion(predicted, target, mask)
    >>> loss.item()
    0.0

    Parameters
    ----------
    mask : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        mask flag.

    References
    ----------
    https://pytorch.org/docs/stable/generated/torch.nn.L1Loss.html

    """

    def __init__(self, mask):
        super(MAELoss, self).__init__()
        if mask:
            self.reg_fn = self.mae_masked()
        else:
            self.reg_fn = self.mae()

    def mae(self):
        mae_loss = nn.L1Loss()

        def loss(y_pred, y_true, mask=None):
            return mae_loss(y_pred, y_true)

        return loss

    def mae_masked(self):
        mae_loss = nn.L1Loss()

        def loss(y_pred, y_true, mask=None):
            return mae_loss(y_pred * mask, y_true * mask)

        return loss

    def forward(self, predicted, target, mask=None):
        """Compute loss between :attr:`predicted` and :attr:`target`.

        :attr:`predicted` and :attr:`target` are tensors of shape :math:`[B,None]`
        if args.mask=True in __init__ :attr:`mask` tensor for shape :math:`[B,None]` will be used for loss computation.

        Parameters
        ----------
        predicted : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Predicted output tensor from a model.
        target : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Ground truth tensor.
        mask : `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            (Optional) Mask tensor to constrain the loss computation.

        Returns
        -------
        `torch.Tensor <https://pytorch.org/docs/stable/tensors.html#torch.Tensor>`_
            Mean Absolute Error loss computed between :attr:`predicted` and :attr:`target`.
        """
        return self.reg_fn(y_pred=predicted, y_true=target, mask=mask)
