"""A standardized abstraction for all data sources."""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from torch.utils.data import Dataset


@dataclass
class EncodingSpec:
    """Describes the index of the encoding and number of unique values it can assume."""

    feature_index: int
    num_vals: int

    def __post_init__(self) -> None:
        """Validates the `EncodingSpec`."""
        if self.num_vals < 2:
            raise ValueError(f'An encoding must contain at least two unique values, {self.num_vals} specified for '
                             f'`feature_index` {self.feature_index}.')
        if self.feature_index < 0:
            raise ValueError(f'`feature_index` must be positive, {self.feature_index} given.')


@dataclass
class DataSourceConfig:
    """A config specifying the properties of the data source.

    Attributes:
    ----------
    feature_channels: int
        The number of channels, exclusive of the time series itself, the data source provides for forecasting.
    forecast_channels: int
         The number of channels to be forecast
    encodings: Sequence[EncodingSpec], optional
        Details regarding each feature embedding (its feature index and cardinality)

    """

    feature_channels: int
    forecast_channels: int
    encodings: Optional[Sequence[EncodingSpec]] = None

    def __post_init__(self) -> None:
        """Validates `DataSourceConfig`.

        Returns
        -------
        None

        """
        if self.encodings:
            for encoding in self.encodings:
                if encoding.feature_index >= self.feature_channels:
                    raise ValueError(f'Embed feature_index {encoding.feature_index} >= # of feature channels'
                                     f'{self.feature_channels}')


class AbstractDataSource(abc.ABC):
    """Interface which all data sources must fulfill."""

    @abc.abstractmethod
    def get_config(self) -> DataSourceConfig:
        """Provides the configuration describing the data source.

        Returns
        -------
        DataSourceConfig
            The number of input channels and the desired prediction horizon

        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_dataset(self,
                    window_size: int,
                    one_hot: bool = False,
                    drop_first: Optional[bool] = None) -> Tuple[Dataset, Dataset]:
        """Provides PyTorch Datasets for training and validation for the given data source.

        Parameters
        ----------
        window_size: int
            The number of samples required to make a forecast
        one_hot: bool, optional
            Whether index encodings should be converted into one-hot encodings, defaults to False
        drop_first: bool, optional
            If one-hot encoding, whether index=0 should map to the zero vector or [1, 0, ...], defaults to False

        Returns
        -------
        Tuple[Dataset, Dataset]
            A tuple of (training dataset, validation dataset) derived from the data source

        """
        raise NotImplementedError
