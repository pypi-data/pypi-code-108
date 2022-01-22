import datetime as dt
from pathlib import Path
from typing import List, Tuple, Union, Dict

import numpy as np
import pandas as pd
import tensorflow as tf
from dateutil import parser


class EXP_1_1_DatasetFactory:  # noqa
    """
    Produces datasets representing every input data used in experiment EXP_1_1.
    Serves from THFP and label data from a well-defined directory and file name structure
    Assumes minutewise ohlcv data available in <basepath>/features/<symbol>
    Assumes labels data available in <basepath>/data/labels
    """

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.thfp_path = self.base_path / 'features' / 'THFP'
        self.labels_path = self.base_path / 'labels' / 'FLR'
        self.rema_path = self.base_path / 'features' / 'REMA'
        self.paths = {
            'REMA': self.rema_path,
            'THFP': self.thfp_path,
            'FLR': self.labels_path
        }

    def get_flr_labels(self, symbol: str, first_day: dt.date, last_day: dt.date):
        """
        Creates a dataset for the given sybol, each record being a 6-dim vector indicating log returns \
        over 1d to 200d periods
        See <ref> for details.
        :return: a function that produces a new dataset for FLRs on each call
        """
        labels_file = list(self.labels_path.glob(f'{symbol}*'))[0]

        # labels_range = str(labels_file).split('_FLR_')[1].split('.')[0]
        # first, last = labels_range.split('_')
        # first, last = parser.isoparse(first).date(), parser.isoparse(last).date()

        first_av, last_av = self.date_range_from_file(str(labels_file), 'FLR')

        labels_dataset = tf.data.TFRecordDataset(str(labels_file))
        labels_dataset = labels_dataset.map(lambda t: tf.io.parse_tensor(t, out_type=tf.float16))
        flr = labels_dataset.map(lambda t: tf.reshape(t, (6,)))

        flr = filter_by_date(flr, first_av, last_av, first_day, last_day)

        return lambda: flr

    def get_thfp_features(self, symbol: str, first_day: dt.date, last_day: dt.date):
        """
        T.H.F.P = "trading hour finger print"
        Creates a dataset for the given sybol, each record being a 14x9x3 tensor \
        indicating the last 14 days trading action history.
        See <ref> for details.
        :return: a function that produces a new dataset for THFP on each call
        """
        thfp_file = list(self.thfp_path.glob(f'{symbol}*'))[0]

        first_av, last_av = self.date_range_from_file(str(thfp_file), 'THFP')

        thfp_dataset = tf.data.TFRecordDataset(str(thfp_file))
        thfp_dataset = thfp_dataset.map(lambda t: tf.io.parse_tensor(t, out_type=tf.float16))
        thfp = thfp_dataset.map(lambda t: tf.reshape(t, (14, 9, 3)))

        thfp = filter_by_date(thfp, first_av, last_av, first_day, last_day)

        return lambda: thfp

    def get_rema_features(self, symbol: str, first_day, last_day):
        rema_file = list(self.rema_path.glob(f'{symbol}_*'))[0]
        first_av, last_av = self.date_range_from_file(str(rema_file), 'REMA')
        if first_day < first_av or last_day > last_av:
            raise ValueError(f'Can only get data from {first_av} to {last_av}')
        rema_dataset = tf.data.TFRecordDataset(str(rema_file))
        rema = rema_dataset.map(lambda t: tf.io.parse_tensor(t, out_type=tf.float16))

        rema = filter_by_date(rema, first_av, last_av, first_day, last_day)

        return lambda: rema

    def get_trend_matrix(self, symbols: List[str], first_day, last_day):
        trend_data = [self.get_rema_features(symbol, first_day, last_day)() for symbol in symbols]

        cutter = np.concatenate([[6 * [0]], np.diag(6 * [1])], axis=0)
        cutter = tf.constant(cutter, dtype=tf.float16)

        all_trends = tf.data.Dataset.zip(tuple(trend_data))
        return lambda: all_trends.map(lambda *t: tf.stack(t, axis=0)).map(lambda t: tf.matmul(t, cutter))

    @staticmethod
    def date_range_from_file(filename: str, category: str) -> Tuple[dt.date, dt.date]:
        date_range = filename.split(f'_{category}_')[1].split('.')[0]
        first, last = date_range.split('_')
        first, last = parser.isoparse(first).date(), parser.isoparse(last).date()
        return first, last

    def common_date_range(self, spec: Dict[str, Union[Union[str, List[str]], Dict[str, List[str]]]]
                          ) -> Tuple[dt.date, dt.date]:
        """
        for a given data specification, like below, returns the first and the last day \
        of the common period of time of all time series in the spec.

        spec: Dict[str, Union[str, List[str]]] = {
            'REMA': ['VIX', 'BTC-USD', 'ARKK', 'ITA'],
            'THFP': ['ITA', 'VNQ'],
            'FLR': 'ITA'
        }
        """
        ranges = []
        for category, symbols in spec.items():
            path = self.paths[category]
            symbols = [symbols] if isinstance(symbols, str) else symbols
            for symbol in symbols:
                filename = str(next(path.glob(f'{symbol}*')))
                first, last = self.date_range_from_file(filename, category)
                ranges.append(set(pd.date_range(first, last)))

        common_days = set.intersection(*ranges)
        return min(common_days).date(), max(common_days).date()


def filter_by_date(ds: tf.data.Dataset, first_av, last_av, first, last) -> tf.data.Dataset:
    """
    If the dataset has all dates from first_av to last_av - in order - return only the data between first and last
    """
    rsup = pd.date_range(first_av, last_av)
    sup = pd.DataFrame(list(rsup), columns=['Date'])

    rsub = pd.date_range(first, last)
    sub = pd.DataFrame(list(rsub), columns=['Date'])
    sub['keep'] = True

    merged = sup.merge(sub, on='Date', how='outer')
    merged.fillna(False, inplace=True)

    array = merged['keep'].to_numpy().tolist()
    filter_ind = tf.data.Dataset.from_tensor_slices(array)
    zipped = tf.data.Dataset.zip((ds, filter_ind))
    filtered = zipped.filter(lambda t, ind: ind)
    return filtered.map(lambda t, _: t)
