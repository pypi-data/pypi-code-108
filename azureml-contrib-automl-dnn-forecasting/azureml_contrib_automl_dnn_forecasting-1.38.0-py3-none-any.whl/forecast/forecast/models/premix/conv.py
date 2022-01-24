"""A causal convolution premix (and its config) of user-defined kernel_size, dilation, stride, and channel count."""

from __future__ import annotations

import dataclasses as dc

import torch

from forecast.models.common.exceptions import TensorShapeException
from forecast.models.common.ops import CausalConv1d, Conv1d
from forecast.models.premix.base import AbstractPremix, AbstractPremixConfig


class ConvPremix(AbstractPremix):
    """A simple causal convolutional premix of user-defined kernel_size, dilation, stride, and channel count.

    Attributes:
    ----------
    config: ConvPremixConfig
        The configuration of the `ConvPremix` instance

    """

    config: ConvPremixConfig

    def __init__(self, config: ConvPremixConfig, output_channels: int):
        """Creates a causal convolutionl premix.

        Parameters
        ----------
        config: ConvPremixConfig
            The config specifying the premix architecture (less output channel count)
        output_channels: int
            The number of output channels in the convolution

        """
        super().__init__(config)
        self._output_channels = output_channels

        if self.config.kernel_size > 1:
            self._conv = CausalConv1d(input_channels=self.config.input_channels,
                                      output_channels=output_channels,
                                      kernel_size=self.config.kernel_size,
                                      dilation=self.config.dilation,
                                      stride=self.config.stride)
            self._conv.conv.weight.data.normal_(0, 0.01)
        else:
            self._conv = Conv1d(in_channels=self.config.input_channels,
                                out_channels=output_channels,
                                kernel_size=self.config.kernel_size,
                                dilation=self.config.dilation,
                                stride=self.config.stride)
            self._conv.weight.data.normal_(0, 0.01)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the causal convolution to the input data.

        Parameters
        ----------
        x: torch.Tensor
            The input to the model

        Returns
        -------
        torch.Tensor
            The output of the causal convolution

        """
        if x.shape[-1] < self.receptive_field:
            raise TensorShapeException(f'Tensor must temporally be of length >= premix receptive field '
                                       f'({self.receptive_field}). Input tensor is of length {x.shape[-1]}.')
        return self._conv(x)

    @property
    def output_channels(self) -> int:
        """The number of channels in the tensor output from the premix.

        Returns
        -------
        int

        """
        return self._output_channels

    @property
    def receptive_field(self) -> int:
        """The receptive field of the causal convolution.

        Returns
        -------
        int
            The receptive field

        """
        return self._conv.receptive_field

    @property
    def is_future_conditioned(self) -> bool:
        """The causal convolution is not conditioned upon values from the forecast period.

        Returns
        -------
        False

        """
        return False


@dc.dataclass
class ConvPremixConfig(AbstractPremixConfig):
    """A config which fully specifies (less output channel count) a causal convolution premix."""

    kernel_size: int
    dilation: int
    stride: int

    def create_premix(self, output_channels: int) -> ConvPremix:
        """Creates a `ConvPremix` according to the config's spec and specified output channels.

        Parameters
        ----------
        output_channels: int
            The desired number of output channels in the causal convolution

        Returns
        -------
        ConvPremix
            The premix object

        """
        if output_channels < 1:
            raise ValueError(f'Conv premix must output >= 1 channel, `output_channels` was set to {output_channels}')
        return ConvPremix(self, output_channels)

    def __post_init__(self) -> None:
        """Validates the configuration and automatically sets the config type.

        Returns
        -------
        None

        """
        super().__post_init__()
        if self.kernel_size < 1:
            raise ValueError('`kernel_size` must be >= 1')
        if self.dilation < 1:
            raise ValueError('`dilation` must be >= 1')
        if self.stride < 1:
            raise ValueError('`stride` must be >= 1')
