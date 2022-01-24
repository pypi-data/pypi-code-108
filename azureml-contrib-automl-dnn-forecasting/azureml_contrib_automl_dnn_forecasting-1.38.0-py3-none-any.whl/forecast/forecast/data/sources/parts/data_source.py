"""A data source an interface to the Parts dataset."""

import copy
import os.path as osp
from typing import Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from forecast.data import FUTURE_IND_KEY
from forecast.data.dataset import TimeSeriesDataset
import forecast.data.date_featurizers as dfeat
from forecast.data.sources.data_source import AbstractDataSource, DataSourceConfig, EncodingSpec
import forecast.data.transforms as tfs
from forecast.data.utils import split_by_count


class PartsDataSource(AbstractDataSource):
    """Parts dataset with featurization matching 'Probabilistic Forecasting with Temporal CNNs'."""

    DEFAULT_FORECAST_HORIZON = 12
    DEFAULT_TEST_LEN = 12
    NUM_PARTS = 1046

    def __init__(self,
                 forecast_horizon: Optional[int] = None,
                 test_split: Optional[int] = None,
                 date_featurizers: Optional[Sequence[dfeat.DateFeaturizer]] = None,
                 eager: bool = False):
        """Instantiates a PartsDataSource.

        Parameters
        ----------
        forecast_horizon: int, optional
            The number of samples to be forecasted, defaults to `DEFAULT_FORECAST_HORIZON`
        test_split: int, optional
            The number of samples to include in the test set, defaults to `DEFAULT_TEST_LEN`
        date_featurizers: Sequence[DateFeaturizer], optional
            A list of featurizers to apply to the date column, defaults to None which signifies MonthOfYear.
        eager: bool, optional
            If True, loads the data upon object creation rather than lazily. Defaults to False.

        """
        super().__init__()
        self._forecast_horizon = forecast_horizon if forecast_horizon else PartsDataSource.DEFAULT_FORECAST_HORIZON
        self._test_len = test_split if test_split else PartsDataSource.DEFAULT_TEST_LEN

        # set our featurizers (performed across the entire dataset)
        if date_featurizers is None:
            self._featurizers = [dfeat.MonthOfYearFeaturizer()]
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
        encodings = [EncodingSpec(feature_index=0, num_vals=PartsDataSource.NUM_PARTS)]
        if self._featurizers:
            encodings += [EncodingSpec(feature_index=i+1, num_vals=f.num_values)  # date features + part encoding
                          for i, f in enumerate(self._featurizers)
                          if f.num_values > 2]

        return DataSourceConfig(feature_channels=1+len(self._featurizers), forecast_channels=1, encodings=encodings)

    def get_dataset(self,
                    window_size: int,
                    one_hot: bool = False,
                    drop_first: Optional[bool] = None) -> Tuple[TimeSeriesDataset, TimeSeriesDataset]:
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
        if self._data is None:
            self._load_data()
        data_train, data_test = split_by_count(self._data, self._test_len, window_size)

        # create datasets
        ds_train = self._build_dataset(data_train.astype(np.float32), window_size, one_hot, drop_first)
        ds_test = self._build_dataset(data_test.astype(np.float32), window_size, one_hot, drop_first)
        return ds_train, ds_test

    def _build_dataset(self,
                       data: np.ndarray,
                       window_size: int,
                       one_hot: bool = False,
                       drop_first: Optional[bool] = None) -> TimeSeriesDataset:
        """Builds a `TimeSeriesDataset` from a given `np.ndarray` of data.

        Parameters:
        -----------
        data: np.ndarray
            The parts data
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
        transform = None
        if one_hot:
            drop = True if drop_first else False
            config = self.get_config()

            assert config.encodings is not None  # there should always at least be a station encoding
            tf_list = [tfs.OneHotEncode([e.feature_index for e in config.encodings],
                                        [e.num_vals for e in config.encodings],
                                        drop_first=drop),
                       tfs.OneHotEncode([e.feature_index for e in config.encodings],
                                        [e.num_vals for e in config.encodings],
                                        drop_first=drop,
                                        key=FUTURE_IND_KEY)]
            transform = tfs.ComposedTransform(tf_list)
        return TimeSeriesDataset(data, window_size, self._forecast_horizon, targets, transform=transform)

    def _load_data(self):
        """Filtering of data from 2674 --> 1046 parts.

        Source: http://www.exponentialsmoothing.net/supplements#data (carparts)

        Note: This filtering follows the process described in 'Forecasting the intermittent demand for slow-moving
        inventories: A modelling approach'.

        """
        # Get the data path
        data_path = osp.join(osp.dirname(osp.realpath(__file__)), 'carparts.csv')
        if not osp.exists(data_path):
            import requests
            r = requests.get('http://www.exponentialsmoothing.net/sites/default/files/carparts.csv')
            with open(data_path, 'wb') as f:
                f.write(r.content)

        # 2674 parts, however we will filter this down to 1046
        df = pd.read_csv(data_path, index_col='Part', parse_dates=True)

        # remove parts without all 51 months of history (2674 --> 2509 parts)
        df = df.dropna()

        # remove parts without at least 10 months of non-zero demand (2509 --> 1347 parts)
        df = df[(df > 0).sum(1) >= 10]

        # remove parts w/o non-zero demand in the first 15 months (1347 --> 1082 parts)
        df = df[df.iloc[:, :15].sum(1) > 0]

        # remove parts w/o non-zero demand in the last 15 months (1082 --> 1046 parts)
        df = df[df.iloc[:, -15:].sum(1) > 0]

        # create multi-index of (part id, month)
        df = df.stack().to_frame()

        # convert to dates and rename
        df.index.set_levels(pd.to_datetime(df.index.levels[-1], format='%b-%y'), level=-1, inplace=True)
        df.index.rename('date', level=-1, inplace=True)

        # rename target
        df.columns = ['target']

        # add integer part index column
        num_parts = len(df.index.levels[0])
        num_dates = len(df) // num_parts
        df['part_index'] = np.repeat(range(num_parts), num_dates)

        if self._featurizers:
            dts = df.index.get_level_values(-1)
            for featurizer in self._featurizers:
                df[featurizer.name] = featurizer(dts)

        assert df['part_index'].nunique() == PartsDataSource.NUM_PARTS
        assert df['part_index'].min() == 0
        assert df['part_index'].max() == PartsDataSource.NUM_PARTS - 1

        self._data = df
