"""Electricity consumption of 370 clients. https://archive.ics.uci.edu/ml/datasets/ElectricityLoadDiagrams20112014."""

import copy
import os.path as osp
from typing import List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from torch.utils.data import Dataset

from forecast.data import FUTURE_IND_KEY
from forecast.data.dataset import TimeSeriesDataset
import forecast.data.date_featurizers as dfeat
from forecast.data.sources.data_source import AbstractDataSource, DataSourceConfig, EncodingSpec
from forecast.data.sources.utils import fetch_zipped_data
import forecast.data.transforms as tfs
from forecast.data.utils import split_by_count


class ElectricityDataSource(AbstractDataSource):
    """Electricity consumption of 370 clients."""

    DEFAULT_FORECAST_HORIZON = 24
    DEFAULT_TEST_LEN = 24 * 7
    NUM_STATIONS = 370
    NUM_TS = 26304

    def __init__(self,
                 forecast_horizon: Optional[int] = None,
                 test_split: Optional[int] = None,
                 date_featurizers: Optional[Sequence[dfeat.DateFeaturizer]] = None,
                 eager: bool = False):
        """Instantiates a ElectricityDataSource.

        Parameters
        ----------
        forecast_horizon: int, optional
            The number of samples to be forecasted, defaults to `DEFAULT_FORECAST_HORIZON`
        test_split: int, optional
            The number of samples to include in the test set, defaults to `DEFAULT_TEST_LEN`
        date_featurizers: Sequence[DateFeaturizer], optional
            A list of featurizers to apply to the date column, defaults to None which signifies: HourOfDay, DayOfWeek,
            DayOfMonth, DayOfYear, and Holiday.
        eager: bool, optional
            If True, loads the data upon object creation rather than lazily. Defaults to False.

        """
        super().__init__()

        # set our forecast horizon and length of test set
        if forecast_horizon:
            self._forecast_horizon = forecast_horizon
        else:
            self._forecast_horizon = ElectricityDataSource.DEFAULT_FORECAST_HORIZON
        self._test_len = test_split if test_split else self.DEFAULT_TEST_LEN

        # set our featurizers (performed across the entire dataset)
        if date_featurizers is None:
            self._featurizers = [dfeat.HourOfDayFeaturizer(),
                                 dfeat.DayOfWeekFeaturizer(),
                                 dfeat.MonthOfYearFeaturizer(),
                                 dfeat.HolidayFeaturizer()]
        elif not isinstance(date_featurizers, Sequence):
            raise TypeError(f'`date_featurizers` should be of type Sequence, is of type {type(date_featurizers)}')
        else:
            self._featurizers = list(copy.deepcopy(date_featurizers))

        self._data: Optional[pd.DataFrame] = None
        if eager:
            self._load_data()

    def get_config(self) -> DataSourceConfig:
        """Provides the configuration describing the data source.

        Returns
        -------
        DataSourceConfig
            The number of input channels and the desired prediction horizon

        """
        encodings = [EncodingSpec(feature_index=0, num_vals=ElectricityDataSource.NUM_STATIONS)]
        if self._featurizers:
            encodings = [EncodingSpec(feature_index=i+1, num_vals=f.num_values)
                         for i, f in enumerate(self._featurizers)
                         if f.num_values > 2]

        return DataSourceConfig(feature_channels=1+len(self._featurizers),  # station_id + any date features
                                forecast_channels=1,
                                encodings=encodings)

    def _build_dataset(self,
                       data: np.ndarray,
                       window_size: int,
                       one_hot: bool = False,
                       drop_first: Optional[bool] = None) -> TimeSeriesDataset:
        """Builds a `TimeSeriesDataset` from a given `np.ndarray` of data.

        Parameters:
        -----------
        data: np.ndarray
            The electricity data
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
            tfs.SubtractOffset(targets=targets)
        ]

        if one_hot:
            drop = True if drop_first else False
            config = self.get_config()

            assert config.encodings is not None  # there should always at least be a station encoding
            ohes: List[tfs.AbstractTransform] = [tfs.OneHotEncode([e.feature_index for e in config.encodings],
                                                                  [e.num_vals for e in config.encodings],
                                                                  drop_first=drop),
                                                 tfs.OneHotEncode([e.feature_index for e in config.encodings],
                                                                  [e.num_vals for e in config.encodings],
                                                                  drop_first=drop,
                                                                  key=FUTURE_IND_KEY)]
            tf_list = ohes + tf_list
        transform = tfs.ComposedTransform(tf_list)
        return TimeSeriesDataset(data, window_size, self._forecast_horizon, targets, transform=transform)

    def get_dataset(self,
                    window_size: int,
                    one_hot: bool = False,
                    drop_first: Optional[bool] = None) -> Tuple[Dataset, Dataset]:
        """Creates training and test datasets from the electricity data.

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
        # implement 24 hour forecasting horizon on the last 7 days of data based on a rolling window approach
        # For validation process TCN -> DeepAR -> https://www.cs.utexas.edu/~rofuyu/papers/tr-mf-nips.pdf
        #   -> https://arxiv.org/pdf/1508.07497.pdf
        if self._data is None:
            self._load_data()

        # split the dataset by an arbitrary date
        data_train, data_test = split_by_count(self._data, self._test_len, window_size)

        ds_train = self._build_dataset(data_train.astype(np.float32), window_size, one_hot, drop_first)
        ds_test = self._build_dataset(data_test.astype(np.float32), window_size, one_hot, drop_first)
        return ds_train, ds_test

    def _load_data(self) -> None:
        """Loads traffic data.

        Source: https://archive.ics.uci.edu/ml/datasets/ElectricityLoadDiagrams20112014

        Note: This filtering approach follows that described in 'Probabilistic Forecasting with Temporal Convolutional
        Networks'.

        """
        # Get the data path
        data_filename = 'LD2011_2014.txt'
        data_path = osp.join(osp.dirname(osp.realpath(__file__)), data_filename)

        # fetch from UCI repository if it does not yet exist
        # WARNING: this is ~250MB compressed, ~700MB uncompressed
        if not osp.exists(data_path):
            fetch_zipped_data(
                data_path,
                'https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip'
            )

        df = pd.read_csv(data_path, index_col=0, sep=';', decimal=',', parse_dates=True, dtype=np.float32)

        # convert from every 15min to every hour by summing the 15min consumption
        df = df.resample('H').sum()

        # filter the data to 2012-2014 and convert to row per customer
        start_dt = pd.datetime(2012, 1, 1)
        end_dt = pd.datetime(2015, 1, 1)
        df = df[(df.index >= start_dt) & (df.index < end_dt)]

        # convert from (Time, TS) --> (MultiIndex(TS, time), 1)
        df = df.T.stack()

        # convert to dataframe
        df = df.to_frame()

        # rename target
        df.columns = ['target']

        assert len(df.index.levels[0]) == ElectricityDataSource.NUM_STATIONS
        assert len(df.index.levels[1]) == ElectricityDataSource.NUM_TS

        # add station embedding (we know rows are sorted by station, so just repeat an integer N times)
        tot_len = len(df)
        ns = ElectricityDataSource.NUM_STATIONS
        assert tot_len % ns == 0
        df['station'] = np.repeat(range(ns), tot_len // ns)

        if self._featurizers:
            dts = df.index.get_level_values(-1)
            for featurizer in self._featurizers:
                df[featurizer.name] = featurizer(dts)

        # store the df
        self._data = df
