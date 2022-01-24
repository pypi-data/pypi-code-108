"""A head (and its config) which forecasts values by applying a linear layer."""

from __future__ import annotations

import dataclasses as dc

import torch
import torch.nn as nn

from forecast.models.forecast_head.base import AbstractForecastHead, AbstractForecastHeadConfig


class UnboundedScalarForecastHead(AbstractForecastHead):
    """A head which forecasts an unbounded scalar value by applying a linear layer.

    Unbounded values are commonly used to forecast a point estimate or a mean/quantile of a probabilistic estimate.
    """

    def __init__(self, config: UnboundedScalarForecastHeadConfig, input_channels: int, dropout_rate: float = 0):
        """Creates an `UnboundedScalarForecastHeadConfig`.

        Parameters
        ----------
        config: UnboundedScalarForecastHeadConfig
            The config specifying the head's architecture
        input_channels: int
            The number of channels of the input to the layer
        dropout_rate: float
            The rate at which dropout is applied within the layer

        """
        super().__init__(config)

        horizon = config.horizon

        self._dropout = nn.Dropout(dropout_rate) if dropout_rate > 0 else nn.Identity()
        self._linear = nn.Linear(input_channels, horizon)
        self._linear.weight.data.normal_(0, 0.01)
        self.op = nn.Sequential(self._dropout, self._linear)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the forecast head to the provided Tensor.

        Parameters
        ----------
        x: torch.Tensor
            The input to the forecast head

        Returns
        -------
        torch.Tensor
            The prediction made by the forecast head

        """
        return self.op(x)

    @property
    def receptive_field(self) -> int:
        """The receptive field of the forecast head.

        Returns
        -------
        1

        """
        return 1

    @property
    def is_future_conditioned(self) -> bool:
        """This forecast head is not conditioned on future values.

        Returns
        -------
        False

        """
        return False


@dc.dataclass
class UnboundedScalarForecastHeadConfig(AbstractForecastHeadConfig):
    """The config for the `UnboundedScalarForecastHead`."""

    def create_head(self, input_channels: int, dropout_rate: float = 0) -> UnboundedScalarForecastHead:
        """Creates an `UnboundedScalarForecastHead`.

        Parameters
        ----------
        input_channels: int
            The number of channels passed to the head.
        dropout_rate: float
            The rate at which dropout should be applied

        Returns
        -------
        UnboundedScalarForecastHead
            A `UnboundedScalarForecastHead` configured according to the specs provided

        """
        if input_channels <= 0:
            raise ValueError('`input_channels` must be > 0')
        if dropout_rate < 0 or dropout_rate >= 1:
            raise ValueError('`dropout_rate` must be between 0 and 1')
        return UnboundedScalarForecastHead(self, input_channels, dropout_rate)
