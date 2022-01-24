"""This module provides abstract base classes from which all premixers (and their configs) should be derived."""

from __future__ import annotations

import abc
import copy
import dataclasses as dc

from forecast.models.common.component import ModelComponentConfig
from forecast.models.common.module import RFModule


class AbstractPremix(RFModule, abc.ABC):
    """The abstract base class from which all premixers are derived.

    Attributes:
    -----------
    config; AbstractPremixConfig
        The config used to generate the premix class

    """

    config: AbstractPremixConfig

    def __init__(self, config: AbstractPremixConfig):
        """Creates an abstract premix and persists its configuration.

        Parameters
        ----------
        config: AbstractPremixConfig
            Configuration of the desired premix module.

        """
        super().__init__()
        self.config = copy.deepcopy(config)

    @property
    @abc.abstractmethod
    def output_channels(self) -> int:
        """The number of channels in the tensor output from the premix.

        Returns
        -------
        int

        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_future_conditioned(self) -> bool:
        """Is the premix conditioned on values from the time period in which the model is forecasting.

        Returns
        -------
        bool

        """
        raise NotImplementedError


@dc.dataclass
class AbstractPremixConfig(ModelComponentConfig, abc.ABC):
    """The abstract base class from which all premix configurations should be derived.

    Attributes:
    -----------
    input_channels: int
        The number of channels which can be used for a model to make its forecast

    """

    input_channels: int

    @abc.abstractmethod
    def create_premix(self, output_channels: int) -> AbstractPremix:
        """Creates a premix whose type corresponds to the config.

        Parameters
        ----------
        output_channels: int
            The number of channels the premix should output

        Returns
        -------
        AbstractPremix
            The premix class as specified by the config and output channels

        """
        raise NotImplementedError

    def __post_init__(self) -> None:
        """Validates the configuration.

        Returns
        -------
        None

        """
        super().__post_init__()
        if self.input_channels < 1:
            raise ValueError('`input_channels` must be >= 1')

    @staticmethod
    def abstract_component_config() -> type:
        """Returns the component's abstract config class."""
        return AbstractPremixConfig
