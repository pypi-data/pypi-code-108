"""This module provides abstract base classes from which all backbones (and their configs) should be derived."""

from __future__ import annotations

import abc
import copy
import dataclasses as dc
import enum

from forecast.models.common.component import ModelComponentConfig
import forecast.models.common.module as module


@dc.dataclass
class AbstractBackboneConfig(ModelComponentConfig, abc.ABC):
    """The abstract base class from which all backbone configurations should be derived."""

    @abc.abstractmethod
    def create_backbone(self, input_channels: int, depth: int, dropout_rate: float = 0) -> AbstractBackbone:
        """Creates a backbone whose type corresponds to the config.

        Parameters
        ----------
        input_channels: int
            The number of channels in the data passed to the backbone
        depth: int
            The depth multiplier of the backbone
        dropout_rate: float, optional
            The rate at which dropout should be applied to the backbone (defaults to 0)

        Returns
        -------
        AbstractBackbone
            The backbone class as specified by the config, input channels, depth multiplier, and dropout rate

        """
        raise NotImplementedError()

    @staticmethod
    def abstract_component_config() -> type:
        """Returns the component's abstract config class."""
        return AbstractBackboneConfig


class AbstractBackbone(module.RFModule):
    """The abstract base class from which all backbones should be derived."""

    config: AbstractBackboneConfig

    def __init__(self, config: AbstractBackboneConfig):
        """Creates an abstract backbone and persists its configuration.

        Parameters
        ----------
        config: AbstractBackboneConfig
            Configuration of the desired backbone module.

        """
        super().__init__()
        self.config = copy.deepcopy(config)

    @property
    @abc.abstractmethod
    def output_channels(self) -> int:
        """Returns the backbone's number of output channels.

        Returns
        -------
        int

        """
        raise NotImplementedError()

    @property
    @abc.abstractmethod
    def is_future_conditioned(self) -> bool:
        """Is the backbone conditioned on values from the time period in which the model is forecasting.

        Returns
        -------
        bool

        """
        raise NotImplementedError()


class MultilevelType(enum.Enum):
    """Types of multilevel functionality which backbones may wish to support."""

    NONE = enum.auto()  # The output of the backbone's last cell is the backbone output
    CELL = enum.auto()  # The concat of the output of all cells in all cell lists is the backbone output
    CELL_LIST = enum.auto()  # The concat of the output of each backbone cell list is the backbone output
