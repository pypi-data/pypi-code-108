"""This module provides abstract base classes from which all forecast heads (and their configs) should be derived."""
from __future__ import annotations

import abc
import copy
import dataclasses as dc

from forecast.models.common.component import ModelComponentConfig
from forecast.models.common.module import RFModule


class AbstractForecastHead(RFModule, abc.ABC):
    """The abstract base class from which all forecast heads should be derived."""

    def __init__(self, config: AbstractForecastHeadConfig):
        """Creates an AbstractForecastHead and persists its configuration.

        Parameters
        ----------
        config: AbstractForecastHeadConfig
            The config of the AbstractForecastHead]

        """
        super().__init__()
        self.config = copy.deepcopy(config)

    @property
    @abc.abstractmethod
    def is_future_conditioned(self) -> bool:
        """Is the forecast head conditioned on values from the time period in which it is forecasting.

        Returns
        -------
        bool

        """
        raise NotImplementedError()


@dc.dataclass
class AbstractForecastHeadConfig(ModelComponentConfig, abc.ABC):
    """The abstract base class from which all configs for forecast heads should be derived.

    Attributes:
    ----------
    horizon: int
        The length (in samples) of the forecast that should be made.

    """

    horizon: int

    @abc.abstractmethod
    def create_head(self, input_channels: int, dropout_rate: float = 0) -> AbstractForecastHead:
        """Creates a forecast head whose type corresponds to the config.

        Parameters
        ----------
        input_channels: int
            The number of channels of the `torch.Tensor` being supplied.
        dropout_rate: float, optional
            The rate at which dropout will be applied in the forecast head (defaults to 0)

        Returns
        -------
        AbstractForecastHead
            A forecast head of the corresponding type configured according to the parameters provided

        """
        raise NotImplementedError()

    def __post_init__(self) -> None:
        """Runs after `__init__` is complete and validates the provided value of horizon."""
        super().__post_init__()

        if self.horizon < 1:
            raise ValueError('`horizon` must be >= 1')

    @staticmethod
    def abstract_component_config() -> type:
        """Returns the component's abstract config class."""
        return AbstractForecastHeadConfig
