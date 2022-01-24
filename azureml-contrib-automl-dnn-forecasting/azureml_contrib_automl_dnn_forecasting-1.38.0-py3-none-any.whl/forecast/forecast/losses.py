"""This module implements the quantile loss, which is used in quantile regression."""

from typing import Sequence, Union

import torch
import torch.nn as nn
import torch.nn.functional as F


class QuantileLoss(nn.Module):
    """This module computes the quantile loss over one or more quantiles.

    Note: This is also known as the pinball loss.

    Attributes:
    -----------
    quantiles: List[float]
        A list of quantiles, between 0 and 1 exclusive, on which the predictions should be evaluated.

    """

    def __init__(self, quantiles: Union[float, Sequence[float]]):
        """Creates a quantile loss PyTorch module.

        Parameters
        ----------
        quantiles: float or List[float]
            One or more quantiles for which the predictions should be evaluated

        """
        super().__init__()
        if isinstance(quantiles, float):
            quantiles = [quantiles]
        elif not isinstance(quantiles, Sequence):
            raise TypeError(f'Invalid type "{type(quantiles)}" for parameter quantiles.')

        quantiles = [float(q) for q in quantiles]
        if not all(0 < q < 1 for q in quantiles):
            raise ValueError('All specified quantiles must fall in the range (0, 1).')

        self.register_buffer('quantiles', torch.tensor(quantiles))

    def forward(self, pred: Union[torch.Tensor, Sequence[torch.Tensor]],
                target: torch.Tensor) -> torch.Tensor:
        """Evaluates the quantile loss for the given predictions.

        Parameters
        ----------
        pred: torch.Tensor or List[torch.Tensor]
            The predictions for each quantile. If pred is a list, each tensor is a time-series at a given quantile.
        target: torch.Tensor
            The target values

        Returns
        -------
        torch.Tensor
            The quantile loss averaged across all quantiles and time-series samples

        """
        # torch.stack requires either a list or tuple
        pred = list(pred) if isinstance(pred, Sequence) else [pred]

        batch_size = pred[0].size()[0]
        num_quantiles = len(self.quantiles)
        assert batch_size == target.size()[0]
        assert len(pred) == num_quantiles

        # before: [[batch_size, num_channel, num_samples] * N_quantiles]
        # after: [N_quantiles, batch_size, num_channel, num_samples]
        p = torch.stack(pred)

        # before: [batch_size, num_channel, num_samples]
        # after: [N_quantiles, batch_size, num_channel, num_samples]
        t = target.expand(self.quantiles.size() + target.size())

        # before: [N_quantiles]
        # after: [N_quantiles, batch_size, num_channel, num_samples]
        q = self.quantiles[:, None, None, None].expand_as(p)

        # Note: we return the mean rather than the sum to normalize over sequence length. This ensures that longer
        # sequences do NOT have an outsized effect.
        return (q * F.relu(t - p) + (-q + 1) * F.relu(p - t)).mean()
