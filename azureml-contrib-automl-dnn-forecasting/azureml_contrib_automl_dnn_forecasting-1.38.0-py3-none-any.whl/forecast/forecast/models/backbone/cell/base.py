"""This module provides abstract base classes from which all cells (and their configs) should be derived."""

from __future__ import annotations

import abc
import copy
import dataclasses as dc
from typing import List, Sequence, Union

import torch

from forecast.models.common.component import ModelComponentConfig
from forecast.models.common.module import RFModule


@dc.dataclass
class AbstractCellConfig(ModelComponentConfig, abc.ABC):
    """The abstract base class from which all cell configurations should be derived.

    Attributes:
    ----------
    num_prev_cell_inputs: int
        The number of previous cells which are passed as input to a given cell

    """

    num_prev_cell_inputs: int

    def __post_init__(self) -> None:
        """Validates `num_prev_cell_inputs` and sets `cell_config_type`.

        Returns:
        -------
        None

        """
        super().__post_init__()
        if self.num_prev_cell_inputs < 1:
            raise ValueError('`num_prev_cell_inputs` must be >= 1')

    @abc.abstractmethod
    def create_cell(self, input_channels: int, dropout_rate: float, prev_cells: CellInputs) -> AbstractCell:
        """Creates a cell whose type corresponds to the config.

        Parameters:
        ----------
        input_channels: int
            The number of channels of the tensor(s) passed to the cell
        dropout_rate: float
            The rate at which dropout should be applied
        prev_cells: CellInputs
            A single cell or list of previous cells whose length equals `num_prev_cell_inputs`

        Returns:
        -------
        AbstractCell
            A cell of the corresponding type configured according to the parameters provided

        """
        raise NotImplementedError()

    @staticmethod
    def abstract_component_config() -> type:
        """Returns the component's abstract config class."""
        return AbstractCellConfig


class AbstractCell(RFModule, abc.ABC):
    """The abstract base class from which all cells are derived."""

    def __init__(self, config: AbstractCellConfig):
        """The abstract base class from which all cells are derived."""
        super().__init__()
        self.config = copy.deepcopy(config)

    def forward(self, x: List[torch.Tensor]) -> torch.Tensor:
        """Applies the cell's structure to a list of tensors and outputs a single tensor.

        Parameters
        ----------
        x: List[torch.Tensor]
            The list of tensors passed to the cell

        Returns
        -------
        torch.Tensor
            The output of the cell

        """
        raise NotImplementedError('Cells derived from `AbstractCell` must implement forward')

    def in_backbone(self) -> bool:
        """Returns whether the cell is contained within the model's backbone (defaults to True).

        Note: This is useful for sentinels (such as `NullCell`) which reside outside the backbone and do not impact
        the cell's receptive field.

        Returns
        -------
        bool
            Whether the cell is within the model's backbone

        """
        return True

    @property
    @abc.abstractmethod
    def is_future_conditioned(self) -> bool:
        """Is the cell conditioned on values from the time period in which the model is forecasting.

        Returns
        -------
        bool

        """
        raise NotImplementedError()


CellInputs = Union[AbstractCell, Sequence[AbstractCell]]
"""The union of an `AbstractCell` or sequence of such. This type is passed to the `create_cell` method in any
config class derived from `AbstractCellConfig`."""


class NullCell(AbstractCell):
    """A sentinel whose presence demarcates a location outside of the backbone."""

    @dc.dataclass
    class _NullCellConfig(AbstractCellConfig):
        def create_cell(self, input_channels: int, dropout_rate: float, prev_cells: CellInputs) -> AbstractCell:
            pass

    def __init__(self) -> None:
        """Creates a NullCell."""
        super().__init__(NullCell._NullCellConfig(num_prev_cell_inputs=1))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        """This should never be invoked; raises an error.

        Parameters:
        ----------
        inputs: torch.Tensor
            A dummy input to match the API spec.

        Returns:
        -------
        torch.Tensor
            A dummy output type to match the API spec

        Raises:
        -------
        NotImplementedError
            Always raises this error as forward should never be invoked on a `NullCell`

        """
        raise NotImplementedError('NullCell should not be invoked during forward/backprop')

    @property
    def receptive_field(self) -> int:
        """A `NullCell` has a receptive field of 1 to indicate it doesn't expand a model's receptive field.

        Returns
        -------
        int
            A receptive field of 1

        """
        return 1

    def in_backbone(self) -> bool:
        """A `NullCell` is by definition not a part of a backbone and therefore returns False.

        Returns
        -------
        bool
            Returns False to indicate it's not a part of the backbone.

        """
        return False

    @property
    def is_future_conditioned(self) -> bool:
        """A `NullCell` is not conditioned on future values as it is never actually executed."""
        return False
