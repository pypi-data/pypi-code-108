"""Common torch operations converted into `RFModule`s."""

import torch
import torch.nn as nn
from torch.nn.utils import weight_norm

from forecast.models.common.module import RFModule


class _RightCrop(nn.Module):
    """Right crops a tensor along the last dimension by `crop_size`."""

    def __init__(self, crop_size: int):
        super().__init__()
        self.crop_size = crop_size

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x[:, :, :-self.crop_size].contiguous()


class Conv1d(nn.Conv1d, RFModule):
    """A 1D convolution as an `RFModule`."""

    def __init__(self, *args, **kwargs):  # type: ignore
        """Creates the Conv1d, see torch.nn.Conv1d for further details."""
        super().__init__(*args, **kwargs)
        if self.stride[0] != 1:
            raise NotImplementedError('Non-unity stride not yet supported in Conv1d')

    @property
    def receptive_field(self) -> int:
        """Returns the receptive field of the 1d convolution.

        Returns
        -------
        int

        """
        return (self.kernel_size[0] - 1) * self.dilation[0] + 1


class CausalConv1d(RFModule):
    """A 1d causal convolution as an `RFModule`."""

    def __init__(self,
                 input_channels: int,
                 output_channels: int,
                 kernel_size: int,
                 dilation: int = 1,
                 stride: int = 1):
        """Creates a 1d causal convolution.

        Parameters
        ----------
        input_channels: int
            The number of channels in the tensor passed to the convolution
        output_channels: int
            The number of channels in the tensor returned from the convolution
        kernel_size: int
            The convolution's kernel size
        dilation: int, optional
            The convolution's dilation factor
        stride: int
            The convolution's stride

        """
        super().__init__()

        self.input_channels = input_channels
        self.output_channels = output_channels

        if kernel_size > 1:
            padding = (kernel_size - 1) * dilation
            self.conv = weight_norm(Conv1d(input_channels, output_channels, kernel_size,
                                           stride=stride, padding=padding, dilation=dilation))
            crop = _RightCrop(padding)
            self.op = nn.Sequential(self.conv, crop)
        else:
            self.op = self.conv

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the causal convolution to the input `torch.Tensor`."""
        return self.op(x)

    @property
    def receptive_field(self) -> int:
        """Returns the causal convolution's receptive field.

        Returns
        -------
        int

        """
        return self.conv.receptive_field


class Dropout(nn.Dropout, RFModule):
    """Dropout as an `RFModule`."""

    def __init__(self, *args, **kwargs):  # type: ignore
        """Creates a dropout layer, see torch.nn.Dropout for more details."""
        super().__init__(*args, **kwargs)

    @property
    def receptive_field(self) -> int:
        """Dropout has a receptive field of 1."""
        return 1


class Linear(nn.Linear, RFModule):
    """A Linear layer as an `RFModule`."""

    def __init__(self, *args, **kwargs):  # type: ignore
        """Creates a linear layer, see torch.nn.Linear for more details."""
        super().__init__(*args, **kwargs)

    @property
    def receptive_field(self) -> int:
        """An linear layer has a receptive field of 1."""
        return 1


class Identity(nn.Identity, RFModule):
    """An identity layer as an `RFModule`."""

    def __init__(self, *args, **kwargs):  # type: ignore
        """Creates an identity layer."""
        super().__init__(*args, **kwargs)

    @property
    def receptive_field(self) -> int:
        """An identity layer has a receptive field of 1."""
        return 1
