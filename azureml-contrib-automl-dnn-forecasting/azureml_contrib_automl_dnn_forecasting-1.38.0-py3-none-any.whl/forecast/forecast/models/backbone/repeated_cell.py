"""A backbone which repeats one or more cell architectures repeatedly."""

from __future__ import annotations

import dataclasses as dc
import enum
from typing import Optional, Sequence, Union

import torch
import torch.nn as nn

from forecast.models.backbone.base import AbstractBackbone, AbstractBackboneConfig, MultilevelType
from forecast.models.backbone.cell.base import AbstractCellConfig, NullCell


class RepeatedCellBackbone(AbstractBackbone):
    """A backbone which repeats a cell (or list of cell) architectures."""

    config: RepeatedCellBackboneConfig

    def __init__(self, config: RepeatedCellBackboneConfig, channels: int, depth: int, dropout_rate: float):
        """Creates a backbone which repeats a cell (or list of cell) architectures.

        Parameters
        ----------
        config: RepeatedCellBackboneConfig
            A configuration specifying the cell architectures, how cells should be repeated, and how the backbone's
            output should be constructed
        channels: int
            The number of input (as well as output) channels in the backbone
        depth: int
            The number of times to repeat the cells. The manner in which cells are repeated is controlled via
            `RepeatedCellBackboneConfig.repeat_mode`
        dropout_rate: float
            The rate at which dropout is applied

        """
        super().__init__(config)

        # persist our configuration
        self.depth = depth
        self.channels = channels
        self.dropout_rate = dropout_rate
        self._multilevel = MultilevelType[config.multilevel]

        rep_mode = RepeatMode[config.repeat_mode]

        # create our cells passing the N previous cells. this is done to allow the backbone's
        # receptive field to be computed
        archs = self.config.cell_configs
        prev_cells = [NullCell() for _ in range(archs[0].num_prev_cell_inputs)]
        self._cell_lists = nn.ModuleList()

        if rep_mode == RepeatMode.OUTER:
            # for OUTER, we concatenate `depth` copies of the provided cell list
            for _ in range(depth):
                cell_list = nn.ModuleList()
                for arch in archs:
                    cell_list.append(arch.create_cell(channels, dropout_rate, prev_cells))
                    prev_cells = prev_cells[1:] + [cell_list[-1]]
                self._cell_lists.append(cell_list)
        elif rep_mode == RepeatMode.INNER:
            # for INNER, we nest lists of N copies of each cell inside the provided cell list
            for arch in archs:
                cell_list = nn.ModuleList()
                for _ in range(depth):
                    cell_list.append(arch.create_cell(channels, dropout_rate, prev_cells))
                    prev_cells = prev_cells[1:] + [cell_list[-1]]
                self._cell_lists.append(cell_list)
        else:
            raise ValueError('Unsupported `repeat_mode` set in `RepeatedCellBackboneConfig`')

    def forward(self, x: torch.Tensor, future_x: Optional[torch.Tensor] = None) -> torch.Tensor:
        """Applies the backbone to `x`.

        Parameters
        ----------
        x: torch.Tensor
            The input passed to the backbone from the premix
        future_x: torch.Tensor, optional
            The future known state from the forecast period passed to the backbone (defaults to None)

        Returns
        -------
        torch.Tensor
            The output of the backbone passed to the forecast head(s)

        """
        fc = self.is_future_conditioned
        if future_x and not fc:
            raise ValueError('` future_x` was passed to the backbone but it is not conditioned upon future state.')
        if not future_x and fc:
            raise ValueError('`future_x` was not passed to the backbone but it is conditioned upon future state.')

        # form list for cells
        inputs = [x] * self.config.cell_configs[0].num_prev_cell_inputs

        # sequentially apply the cells while saving the output tensors
        out_tensors = []
        for cell_list in self._cell_lists:
            # we shouldn't have an empty cell_list
            assert cell_list

            for cell in cell_list:
                cell_out = cell(inputs, future_x) if cell.is_future_conditioned else cell(inputs)

                # pop the head and append the cell's output for the next cell's input
                inputs = inputs[1:] + [cell_out]

                if self._multilevel == MultilevelType.CELL:
                    # if multilevel type is CELL, we will concatenate every cell for every repetition of the cell list
                    out_tensors.append(cell_out)

            if self._multilevel == MultilevelType.CELL_LIST:
                # if multilevel type is CELL_LIST, we will concatenate the last cell from every "inner cell list"
                # note: the meaning of "inner cell list" varies based on `repeat_mode`
                out_tensors.append(cell_out)

        # flatten into an N x 1 x out_channel feature vector
        # out_channel is either num_channels (MultilevelType.NONE) or
        # num_channels * num_cells (MultilevelType.CELL) or
        # num_channels * num_cell_lists (MultilevelType.CELL_LIST)
        if self._multilevel in [MultilevelType.CELL, MultilevelType.CELL_LIST]:
            out = torch.cat(out_tensors, dim=1)[:, None, :, -1]
        elif self._multilevel == MultilevelType.NONE:
            out = cell_out[:, None, :, -1]
        else:
            raise NotImplementedError(f'MultilevelType {self._multilevel} not implemented in `forward`')
        return out

    @property
    def receptive_field(self) -> int:
        """The receptive field of the backbone.

        Returns:
        --------
        int

        """
        if self._multilevel == MultilevelType.NONE:
            return self._cell_lists[-1][-1].receptive_field
        elif self._multilevel == MultilevelType.CELL_LIST:
            return max(cell_list[-1].receptive_field for cell_list in self._cell_lists)
        elif self._multilevel == MultilevelType.CELL:
            return max(c.receptive_field for cell_list in self._cell_lists for c in cell_list)
        else:
            raise NotImplementedError(f'MultilevelType {self._multilevel} not implemented in `receptive_field`')

    @property
    def output_channels(self) -> int:
        """The number of channels in the backbone's output.

        Returns:
        --------
        int

        """
        if self._multilevel == MultilevelType.NONE:
            return self.channels
        elif self._multilevel == MultilevelType.CELL_LIST:
            return len(self._cell_lists) * self.channels
        elif self._multilevel == MultilevelType.CELL:
            return len(self._cell_lists) * len(self._cell_lists[0]) * self.channels
        else:
            raise NotImplementedError(f'MultilevelType {self._multilevel} not implemented in `output_channels`')

    @property
    def is_future_conditioned(self) -> bool:
        """Is the backbone conditioned on future state (as determined by its cells).

        Returns:
        --------
        bool

        """
        return any(c.is_future_conditioned for cell_list in self._cell_lists for c in cell_list)


class RepeatMode(enum.Enum):
    """Determines the depth multiplier supplied to `create_backbone` should be interpreted.

    Given my_list = [cell_1, cell_2, ...],
        INNER is equivalent to [[elem] * depth for elem in my_list]
        OUTER is equivalent to [my_list for _ in range(depth)]

    """

    INNER = enum.auto()
    OUTER = enum.auto()


@dc.dataclass
class RepeatedCellBackboneConfig(AbstractBackboneConfig):
    """The configuration which specifies the structure of a `RepeatedCellBackbone`.

    Attributes:
    -----------
    cell_configs: Union[AbstractCellConfig, Sequence[AbstractCellConfig]]
        The config(s) of one or more cells which should be repeated
    multilevel: str
        How the cell's outputs are combined to form the backbone's output:
            none: the last cell's output is what is passed to the forecast heads
            cell_list: the output of every cell list is concatenated and passed to the forecast heads
            cell: the output of every cell is concatenated and passed to the forecast heads
    repeat_mode: str
        How the cells are repeated within the backbone
            inner: equivalent to `[[cell_config] * depth for cell_config in cell_configs]`
            outer: equivalent to `[cell_configs for _ in range(depth)]`

    """

    cell_configs: Union[AbstractCellConfig, Sequence[AbstractCellConfig]]
    multilevel: str
    repeat_mode: str

    def __post_init__(self) -> None:
        """Validates the configuration."""
        super().__post_init__()
        if not isinstance(self.cell_configs, Sequence):
            self.cell_configs = [self.cell_configs]

        self.multilevel = self.multilevel.upper()
        if self.multilevel not in MultilevelType.__members__:
            raise ValueError('Invalid value for `multilevel`')

        self.repeat_mode = self.repeat_mode.upper()
        if self.repeat_mode not in RepeatMode.__members__:
            raise ValueError('Invalid value for `repeat_mode`')

        assert all([c.num_prev_cell_inputs == self.cell_configs[0].num_prev_cell_inputs for c in self.cell_configs])

    def create_backbone(self, input_channels: int, depth: int, dropout_rate: float = 0) -> RepeatedCellBackbone:
        """Creates a backbone of width `input_channels` and repeat count `depth` with dropout applied at dropout_rate.

        Parameters
        ----------
        input_channels: int
            The number channels in the tensor passed to the backbone
        depth: int
            How many times the cells should be repeated
        dropout_rate: float
            The rate at which dropout should be applied

        Returns
        -------
        RepeatedCellBackbone
            The backbone configured as specified

        """
        if input_channels < 1:
            raise ValueError('`input_channels` must be > 1')
        if depth < 1:
            raise ValueError('`depth` must be > 1')
        if dropout_rate < 0 or dropout_rate >= 1:
            raise ValueError('`dropout_rate` must be between 0 and 1')
        return RepeatedCellBackbone(self, input_channels, depth, dropout_rate)
