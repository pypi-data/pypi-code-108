"""A residual cell (and its config) with a user-configurable number of casual convolutions."""

from __future__ import annotations

import dataclasses as dc
from typing import List, Sequence

import torch
import torch.nn as nn
import torch.nn.functional as F

from forecast.models.backbone.cell.base import AbstractCell, AbstractCellConfig, CellInputs, NullCell
from forecast.models.common.ops import CausalConv1d, Dropout, Identity


class CausalConvResidCell(AbstractCell):
    """A residual cell with a configurable number of internal causal convolutions.

    Attributes:
    -----------
    config: CausalConvResidCellConfig
        The configuration specifying the properties of the cell's convolutions (dilation, count, etc)
    channels: int
        The number of channels the cell should expect as both input and output
    dropout_rate: float
        The rate at which dropout should be applied within the cell

    """

    def __init__(self,
                 config: CausalConvResidConfig,
                 input_channels: int,
                 dropout_rate: float,
                 prev_cells: CellInputs):
        """Creates a residual casual convolution cell.

        Parameters
        ----------
        config: CausalConvResidConfig
            The configuration specifying the properties of the cell's convolutions (dilation, count, etc)
        input_channels: int
            The number of channels the cell should expect as input and also output
        dropout_rate: float
            The rate at which dropout should be applied within the cell
        prev_cells: Sequence[AbstractCell] or AbstractCell
            A single abstract cell (either in a list or as itself); used for computing the cell's receptive field

        """
        super().__init__(config)

        if isinstance(prev_cells, Sequence):
            assert len(prev_cells) == 1, 'prev_cells must be of length 1 for `CausalConvResidCell`'
            prev_cell = prev_cells[0]
        else:
            prev_cell = prev_cells

        self.channels = input_channels
        self.dropout_rate = dropout_rate

        # create our ops
        convs = []
        do = []
        relus = []
        for _ in range(config.num_convs):
            c = CausalConv1d(input_channels, input_channels, config.kernel_size, config.dilation, config.stride)
            c.conv.weight.data.normal_(0, 0.01)
            convs.append(c)
            do.append(Dropout(dropout_rate) if dropout_rate > 0 else Identity())
            relus.append(nn.ReLU())

        # fold them into a list of lists
        ops = zip(convs, do, relus)

        # flatten the list of lists
        self._ops = nn.Sequential(*[op for sublist in ops for op in sublist])

        self._receptive_field = sum(c.receptive_field for c in convs) - (len(convs) - 1)
        if not isinstance(prev_cell, NullCell):
            self._receptive_field += prev_cell.receptive_field - 1

    def forward(self, x: List[torch.Tensor]) -> torch.Tensor:
        """Applies the cell to the input tensor.

        Parameters
        ----------
        x: List[torch.Tensor]
            A list of length 1 whose tensor will be transformed by the cell

        Returns
        -------
        torch.Tensor
            The tensor that results from transforming the input tensor by this cell

        """
        assert len(x) == 1
        x = x[0]
        out = self._ops(x)
        return F.relu(out + x)

    @property
    def receptive_field(self) -> int:
        """The receptive field of this cell starting at the root of the backbone.

        Returns
        -------
        int
            The receptive field

        """
        return self._receptive_field

    @property
    def is_future_conditioned(self) -> bool:
        """A residual causal convolution cell is not conditioned upon future input.

        Returns
        -------
        False

        """
        return False


@dc.dataclass
class CausalConvResidConfig(AbstractCellConfig):
    """Config for a `CausalConvResidCell`."""

    kernel_size: int
    dilation: int
    stride: int
    num_convs: int = 2

    def create_cell(self, input_channels: int, dropout_rate: float, prev_cells: CellInputs) -> CausalConvResidCell:
        """Instantiates a cell based on the specified config.

        Parameters
        ----------
        input_channels: int
            The number of channels the cell should expect as input and also output
        dropout_rate: float
            The rate at which dropout should be applied within the cell
        prev_cells: Sequence[AbstractCell] or AbstractCell
            A single abstract cell (either in a list or as itself); used for computing the cell's receptive field

        Returns
        -------
        CausalConvResidCell
            A cell matching the desired specifications

        """
        return CausalConvResidCell(self, input_channels, dropout_rate, prev_cells)

    def __post_init__(self) -> None:
        """Validates the cell's config."""
        super().__post_init__()
        if self.kernel_size < 1:
            raise ValueError('`kernel_size` must be >= 1')
        if self.stride < 1:
            raise ValueError('`stride` must be >= 1')
        if self.dilation < 1:
            raise ValueError('`dilation` must be >= 1')
        if self.num_convs < 1:
            raise ValueError('`num_convs` must be >= 1')
        if self.num_prev_cell_inputs != 1:
            raise ValueError('`num_prev_cell_inputs` must be 1 for class `CausalConvResidConfig`')
