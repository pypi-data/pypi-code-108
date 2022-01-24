"""Supplies Github daily active user data for evaluating forecasting models."""

import copy
import os.path as osp
from typing import List, Optional, Sequence, Tuple
import warnings

import numpy as np
import pandas as pd
from torch.utils.data import Dataset

from forecast.data import FUTURE_IND_KEY
from forecast.data.dataset import TimeSeriesDataset
import forecast.data.date_featurizers as dfeat
from forecast.data.sources.data_source import AbstractDataSource, DataSourceConfig, EncodingSpec
import forecast.data.transforms as tfs
from forecast.data.utils import split_by_count


class GithubDataSource(AbstractDataSource):
    """A dataset containing Github daily active users."""

    DEFAULT_FORECAST_HORIZON = 90
    DEFAULT_TEST_LEN = 454

    def __init__(self,
                 forecast_horizon: Optional[int] = None,
                 test_split: Optional[int] = None,
                 date_featurizers: Optional[Sequence[dfeat.DateFeaturizer]] = None,
                 eager: bool = False):
        """Instantiates a GithubDataSource.

        Parameters
        ----------
        forecast_horizon: int, optional
            The number of samples to be forecasted, defaults to `DEFAULT_FORECAST_HORIZON`
        test_split: int, optional
            The number of samples to include in the test set, defaults to `DEFAULT_TEST_LEN`
        date_featurizers: Sequence[DateFeaturizer], optional
            A list of featurizers to apply to the date column, defaults to None which signifies: DayOfWeek,
            DayOfMonth, DayOfYear, and Holiday.
        eager: bool, optional
            If True, loads the data upon object creation rather than lazily. Defaults to False.

        """
        super().__init__()
        self._forecast_horizon = forecast_horizon if forecast_horizon else GithubDataSource.DEFAULT_FORECAST_HORIZON
        self._test_len = test_split if test_split else GithubDataSource.DEFAULT_TEST_LEN

        # set our featurizers (performed across the entire dataset)
        if date_featurizers is None:
            self._featurizers = [dfeat.DayOfWeekFeaturizer(),
                                 dfeat.MonthOfYearFeaturizer(),
                                 dfeat.HolidayFeaturizer()]
        elif not isinstance(date_featurizers, Sequence):
            raise TypeError(f'`date_featurizers` should be of type Sequence, is of type {type(date_featurizers)}')
        else:
            self._featurizers = list(copy.deepcopy(date_featurizers))

        self._data: Optional[pd.DataFrame] = None
        if eager:
            self._load_data()

    def _load_data(self) -> None:
        """Loads the DAU data.

        Returns:
        --------
        None

        """
        # Get the data path
        data_path = osp.join(osp.dirname(osp.realpath(__file__)), 'github_dau_2011-2018.csv')

        # Get data
        df = pd.read_csv(data_path, index_col='date', parse_dates=True)
        assert bool(df.isnull().any().any()) is False

        if self._featurizers:
            dts = df.index
            for featurizer in self._featurizers:
                df[featurizer.name] = featurizer(dts)

        self._data = df

    def _build_dataset(self,
                       data: np.ndarray,
                       window_size: int,
                       one_hot: bool = False,
                       drop_first: Optional[bool] = None) -> TimeSeriesDataset:
        """Builds a `TimeSeriesDataset` from a given `np.ndarray` of data.

        Parameters:
        -----------
        data: np.ndarray
            The DAU data
        window_size: int
            The number of samples required to make a forecast
        one_hot: bool, optional
            Whether embeddable variables should be converted to a one-hot encoding, defaults to False
        drop_first: bool or None, optional
            If `one_hot` is True, determines whether index=0 --> the 0 vector or [1, 0, ...]. Only valid if `one_hot`
            is True. Defaults to None.

        """
        if drop_first is not None and not one_hot:
            raise ValueError('`drop_first` supplied but is only applicable if `one_hot` is True')

        targets = [0]
        tf_list: List[tfs.AbstractTransform] = [
            tfs.LogTransform(offset=1.0, targets=targets),
            tfs.SubtractOffset(targets=targets),
            tfs.ToTensor()
        ]

        config = self.get_config()
        if one_hot and config.encodings:
            # tell mypy that we have encodings
            drop = True if drop_first else False
            ohes: List[tfs.AbstractTransform] = [
                tfs.OneHotEncode([e.feature_index for e in config.encodings],
                                 [e.num_vals for e in config.encodings],
                                 drop_first=drop),
                tfs.OneHotEncode([e.feature_index for e in config.encodings],
                                 [e.num_vals for e in config.encodings],
                                 drop_first=drop,
                                 key=FUTURE_IND_KEY)
            ]
            tf_list = ohes + tf_list
        elif one_hot:
            warnings.warn('`one_hot` specified but ignored as data source contains no encodable variables.')

        transform = tfs.ComposedTransform(tf_list)
        return TimeSeriesDataset(data, window_size, self._forecast_horizon, targets, transform=transform)

    def get_dataset(self,
                    window_size: int,
                    one_hot: bool = False,
                    drop_first: Optional[bool] = None) -> Tuple[Dataset, Dataset]:
        """Creates training and test datasets from the Github DAU data.

        Parameters:
        -----------
        window_size: int
            The number of samples required to make a forecast
        one_hot: bool, optional
            Whether embeddable variables should be converted to a one-hot encoding, defaults to False
        drop_first: bool or None, optional
            If `one_hot` is True, determines whether index=0 --> the 0 vector or [1, 0, ...]. Only valid if `one_hot`
            is True. Defaults to None.

        """
        if self._data is None:
            self._load_data()

        # split the dataset by an arbitrary date
        data_train, data_test = split_by_count(self._data, self._test_len, window_size)

        # build the datasets
        ds_train = self._build_dataset(data_train.astype(np.float32), window_size, one_hot, drop_first)
        ds_test = self._build_dataset(data_test.astype(np.float32), window_size, one_hot, drop_first)
        return ds_train, ds_test

    def get_config(self) -> DataSourceConfig:
        """Returns the configuration specifying the properties of the Github DAU data."""
        encodings: Optional[List[EncodingSpec]]
        if self._featurizers:
            num_date_features = len(self._featurizers)
            encodings = [EncodingSpec(feature_index=i, num_vals=f.num_values) for i, f in enumerate(self._featurizers)
                         if f.num_values > 2]
        else:
            num_date_features = 0
            encodings = None

        return DataSourceConfig(feature_channels=num_date_features,
                                forecast_channels=1,
                                encodings=encodings)
