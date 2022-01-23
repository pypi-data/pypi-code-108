import torch
import torch.nn as nn

from torch.distributions.normal import Normal


class NLL_Loss(nn.Module):
    r"""Creates a criterion that minimizes Negative Log Liklihood element-wise (with mask support) each element between the input :math:`X` and target :math:`Y`.

    Mean Squared Error between inputs :math:`\hat{Y}` and :math:`Y` with mask :math:`M` is computed as:

    :math:`\hat{Y}` has twice the indices as :math:`Y` where every index pair :math:`(2j,2j+1)`
    for :math:`j \in \{ k | 1 \leq k \leq 2N \}` in :math:`\hat{Y}` denotes a
    Normal Distribution :math:`\mathcal{N}_j` such as :-

    For :math:`j \in \{ k | 1 \leq k \leq 2N \}`
    :math:`\mathcal{N}_{j}` has mean :math:`\mu_{j}= \hat{Y}_{2j}` and
    standard deviation :math:`\sigma_{j}= \hat{Y}_{2j+1}` :math:`\therefore`,

    .. math:: p(Y_{j} | X) = \mathcal{N}_{j}(Y_{j},\mu_{j},\sigma_{j}^{2}) = \frac{1}{\sqrt{2\pi\sigma_{j}^{2}}{}} \exp(\frac{-1}{2}\frac{(Y_{j}-\mu_{j})^{2}}{\sigma_{j}^{2}})
    where :math:`X` is the input corresponding to ground truth :math:`Y`.

    .. math:: NLL_{j}(\hat{Y}_{(2j,2j+1)},Y_{j}) = - \frac {1}{M} \sum\limits_{i=1}^{M} \log p(Y_{j} | X_{i}) \cdot \hat{M}_{(i,j)}
    .. math:: NLL(\hat{Y},Y) = \sum_{j=1}^{N} NLL_{j}(\hat{Y}_{(2j,2j+1)},Y_{j})

    where :math:`M` is no. of samples.

    where :math: mask `\hat{M}` is binary tensor.

    reduction='mean', If args.mask=True masked version will be used.

    If args.mask=False :math:`\hat{M}`=torch.ones_like(:math:`X`).

    Parameters
    ----------
    mask : `boolean <https://docs.python.org/3/library/functions.html#bool>`_
        mask flag.
    epsilon : `float <https://docs.python.org/3/library/functions.html#float>`_
        epsilon

    Examples
    --------
    >>> criterion = NLL_Loss(False)
    >>> predicted = torch.ones(2, 32)
    >>> target = torch.zeros(2, 16)
    >>> loss = criterion(predicted, target)
    >>> loss.item()
    11.3515

    >>> mask = torch.zeros((2,16), dtype=torch.float32)
    >>> criterion = NLL_Loss(True)
    >>> predicted = torch.ones(2, 32)
    >>> target = torch.zeros(2, 16)
    >>> loss = criterion(predicted, target, mask)
    >>> loss.item()
    11.3515 

    """

    def __init__(self, mask, epsilon=1e-4):
        super(NLL_Loss, self).__init__()
        self.reg_fn = self.nll

        self.mask = mask
        self.epsilon = epsilon

    def nll(self, y_pred, y_true, mask=None):
        loss = torch.zeros_like(y_true)
        cnt = 0

        for i in range(0, y_pred.shape[1], 2):
            loss[:, cnt] = Normal(loc=y_pred[:, i],
                                  scale=torch.clamp(torch.exp(y_pred[:, i + 1]) + self.epsilon,
                                                    self.epsilon, 1e+4),
                                  validate_args=False).log_prob(y_true[:, cnt])
            cnt += 1
            if self.mask:
                loss[:, cnt] = loss[:, cnt] * mask[:, cnt]
        loss = torch.mean(loss, dim=0)

        return -1 * torch.sum(loss)

    def forward(self, predicted, target, mask=None):
        """Compute loss between :attr:`predicted` and :attr:`target`.

        :attr:`predicted` and :attr:`target` are tensors of shape :math:`[B,2N]` and :math:`[B,N]` respectively.
        if args.mask=True in __init__ :attr:`mask` tensor for shape :math:`[B,N]` will be used for loss computation.

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
            Negative Log Liklihood (element-wise) loss computed between :attr:`predicted` and :attr:`target`.
        """
        return self.reg_fn(y_true=predicted, y_pred=target, mask=mask)
