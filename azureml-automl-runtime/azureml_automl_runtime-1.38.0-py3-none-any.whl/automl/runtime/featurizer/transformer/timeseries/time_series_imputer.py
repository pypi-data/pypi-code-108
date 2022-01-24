# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Impute missing data in time-series specific ways, such as interpolation."""
from typing import Any, cast, Dict, List, Optional, Set, Tuple, Union
from warnings import warn

from collections import OrderedDict
import logging
import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from azureml._common._error_definition import AzureMLError
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesTransCannotInferFreq,
    MissingColumnsInData,
    TimeseriesInputIsNotTimeseriesDf)
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.forecasting_exception import (ForecastingDataException)
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.shared.forecasting_utils import get_period_offsets_from_dates
from azureml.automl.runtime.shared.time_series_data_frame import TimeSeriesDataFrame
from azureml.automl.runtime.shared.types import DataSingleColumnInputType

from .forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer
from .forecasting_constants import HORIZON_COLNAME

logger = logging.getLogger(__name__)


class TimeSeriesImputer(AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer):
    """
    Imputation transformer for imputing the missing values of data frame columns.

    .. _pandas.Series.interpolate: https://pandas.pydata.org/pandas-docs/
                                stable/generated/pandas.Series.interpolate.html
    .. _pandas.Series.fillna: https://pandas.pydata.org/pandas-docs/stable/
                                generated/pandas.Series.fillna.html
    .. _pandas.DateOffset: https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects

    :param input_column:
        The name(s) of the column(s) need(s) to be imputed.
    :type input_column: str or list[str]

    :param option:
        One of {'interpolate', 'fillna'}.
        The 'interpolate' and 'fillna' options have additional
        parameters that specify their operation.
    :type option: str

    :param method:
        Can be used for option 'interpolate' or 'fillna', see
        pandas.Series.interpolate or pandas.Series.fillna respectively
        for more information. In addition, dictionary input in the form
        of {pandas.Series.fillna method: [applicable cols]} is accepted
        for option 'fillna'.
    :type method: str, dict

    :param limit:
        Can be used for option 'interpolate' or 'fillna', see
        pandas.Series.interpolate or pandas.Series.fillna respectively
        for more information.
    :type limit: str

    :param value:
        Can be used for option 'fillna', see pandas.Series.fillna
        for more information.

    :param limit_direction:
        can be used for option 'interpolate', see pandas.Series.interpolate
        for more information.
    :type limit_direction: str

    :param order:
        can be used for option 'interpolate', see pandas.Series.interpolate
        for more information.
    :type order: str

    :param freq:
        Time series frequency.
        If the freq is string, this string needs to be a pandas Offset Alias.
        See pandas.tseries.offsets.DateOffset for more information.
    :type freq: str or pandas.tseries.offsets.DateOffset

    :param origin:
        If provided, the datetime will be filled back to origin for
        all grains.
    :type origin: str
    :param end:
        If provided, the datetime will be filled up to end for all grains.
    :type end: string

    :param impute_by_horizon:
        See documentation for TimeSeriesImputer.transform() for more
        information.
    :type impute_by_horizon: bool

    Examples:
    Construct a sample dataframe: df1
    Notice that df1 is not a regular time series, because for store 'a',
    the row for date '2017-01-03' is missing.

    >>> data1 = pd.DataFrame(
    ...  {'store': ['a', 'a', 'b', 'b', 'c', 'c', 'c', 'd',
    ...            'd', 'd', 'd', 'd', 'd', 'd', 'd'],
    ...   'date': pd.to_datetime(
    ...      ['2017-01-02', '2017-01-04', '2017-01-01', '2017-01-02',
    ...       '2017-01-01', '2017-01-02', '2017-01-03', '2017-01-01',
    ...       '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05',
    ...       '2017-01-06', '2017-01-07', '2017-01-08']),
    ...   'sales': [1, np.nan, 2, np.nan, 6, 7, np.nan, 10, 11, 15, 13, 14,
    ...             np.nan, np.nan, 15],
    ...   'price': [np.nan, 3, np.nan, 4, 3, 6, np.nan, 2, 6, 3, 5, 5,
    ...             np.nan, np.nan, 6]})
    >>> df1 = TimeSeriesDataFrame(data1, grain_colnames=['store'],
    ...                           time_colname='date', ts_value_colname='sales')
    >>> df1
    >>>                price  sales
    >>> date       store
    2017-01-02 a        nan   1.00
    2017-01-04 a       3.00    nan
    2017-01-01 b        nan   2.00
    2017-01-02 b       4.00    nan
    2017-01-01 c       3.00   6.00
    2017-01-02 c       6.00   7.00
    2017-01-03 c        nan    nan
    2017-01-01 d       2.00  10.00
    2017-01-02 d       6.00  11.00
    2017-01-03 d       3.00  15.00
    2017-01-04 d       5.00  13.00
    2017-01-05 d       5.00  14.00
    2017-01-06 d        nan    nan
    2017-01-07 d        nan    nan
    2017-01-08 d       6.00  15.00

    If you run infer_freq, the 'regular_ts' attribute is False,
    with inferred frequency 'D'.

    >>> df1.infer_freq() # doctest: +SKIP
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    {'regular_ts': False, 'freq': 'D'}

    >>> sorted(df1.infer_freq().items())
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    [('freq', 'D'), ('regular_ts', False)]

    Impute df1 for single column 'sales' with option 'default'
    Notice here, for store 'a', the missing row for date '2017-01-03'
    is added and imputed as well.
    Also by default, the freq that is used to fill in the missing date
    is the inferred frequency from df1.infer_freq(), in this case: 'D'

    >>> imputer1 = TimeSeriesImputer(input_column='sales', option='default')
    >>> imputer1.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.


    >>>      date  price      sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    If you want to specify the freq explicitly, you can also use the
    'freq' key argument to pass the freq, since in some cases the inferred
    frequency might not be exact, such as no frequency is inferred from
    any time series, or there are multiple frequencies inferred and the
    one chosen is not the one you want.

    >>> imputer2 = TimeSeriesImputer(input_column='sales', option='default',
    ...                              freq='D')
    >>> imputer2.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price      sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    The default option is just the same as set option='interpolate',
    method='linear' and limit_direction='both'

    >>> imputer3 = TimeSeriesImputer(input_column='sales',
    ...                              option='interpolate', method='linear',
    ...                              limit_direction='both')
    >>> imputer3.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   7.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  14.333333     d
    14 2017-01-07    NaN  14.666667     d
    15 2017-01-08    6.0  15.000000     d

    You can also impute for list of columns. Here, impute df1 for both
    'sales' and 'price' columns.

    >>> imputer4 = TimeSeriesImputer(input_column=['sales', 'price'],
    ...                              option='default')
    >>> imputer4.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02  3.000000   1.000000     a
    1  2017-01-03  3.000000   1.000000     a
    2  2017-01-04  3.000000   1.000000     a
    3  2017-01-01  4.000000   2.000000     b
    4  2017-01-02  4.000000   2.000000     b
    5  2017-01-01  3.000000   6.000000     c
    6  2017-01-02  6.000000   7.000000     c
    7  2017-01-03  6.000000   7.000000     c
    8  2017-01-01  2.000000  10.000000     d
    9  2017-01-02  6.000000  11.000000     d
    10 2017-01-03  3.000000  15.000000     d
    11 2017-01-04  5.000000  13.000000     d
    12 2017-01-05  5.000000  14.000000     d
    13 2017-01-06  5.333333  14.333333     d
    14 2017-01-07  5.666667  14.666667     d
    15 2017-01-08  6.000000  15.000000     d

    You can also set options to 'interpolate' and use key arguments such as
    'method', 'limit', 'limit_direction' and 'order'
    from pandas.Series.interpolate
    Note if the specific method used does not apply to some of the grains,
    the default linear interpolation is used for those grains.

    >>> imputer5 = TimeSeriesImputer(input_column=['sales'],
    ...                              option='interpolate', method='barycentric')
    >>> imputer5.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN   1.000000     a
    1  2017-01-03    NaN   1.000000     a
    2  2017-01-04    3.0   1.000000     a
    3  2017-01-01    NaN   2.000000     b
    4  2017-01-02    4.0   2.000000     b
    5  2017-01-01    3.0   6.000000     c
    6  2017-01-02    6.0   7.000000     c
    7  2017-01-03    NaN   8.000000     c
    8  2017-01-01    2.0  10.000000     d
    9  2017-01-02    6.0  11.000000     d
    10 2017-01-03    3.0  15.000000     d
    11 2017-01-04    5.0  13.000000     d
    12 2017-01-05    5.0  14.000000     d
    13 2017-01-06    NaN  26.904762     d
    14 2017-01-07    NaN  42.428571     d
    15 2017-01-08    6.0  15.000000     d

    You can also set options to 'fillna' and use use key arguments such as
    'method', 'value' and 'limit'methods from pandas.Series.fillna

    >>> imputer6 = TimeSeriesImputer(input_column=['sales'], option='fillna', method='ffill')
    >>> imputer6.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    1.0     a
    2  2017-01-04    3.0    1.0     a
    3  2017-01-01    NaN    2.0     b
    4  2017-01-02    4.0    2.0     b
    5  2017-01-01    3.0    6.0     c
    6  2017-01-02    6.0    7.0     c
    7  2017-01-03    NaN    7.0     c
    8  2017-01-01    2.0   10.0     d
    9  2017-01-02    6.0   11.0     d
    10 2017-01-03    3.0   15.0     d
    11 2017-01-04    5.0   13.0     d
    12 2017-01-05    5.0   14.0     d
    13 2017-01-06    NaN   14.0     d
    14 2017-01-07    NaN   14.0     d
    15 2017-01-08    6.0   15.0     d

    >>> imputer7 = TimeSeriesImputer(input_column=['sales'], option='fillna',
    ...                              value=0)
    >>> imputer7.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    0.0     a
    2  2017-01-04    3.0    0.0     a
    3  2017-01-01    NaN    2.0     b
    4  2017-01-02    4.0    0.0     b
    5  2017-01-01    3.0    6.0     c
    6  2017-01-02    6.0    7.0     c
    7  2017-01-03    NaN    0.0     c
    8  2017-01-01    2.0   10.0     d
    9  2017-01-02    6.0   11.0     d
    10 2017-01-03    3.0   15.0     d
    11 2017-01-04    5.0   13.0     d
    12 2017-01-05    5.0   14.0     d
    13 2017-01-06    NaN    0.0     d
    14 2017-01-07    NaN    0.0     d
    15 2017-01-08    6.0   15.0     d

    Sometime, you might want to fill values up to some eariler date or down
    to some later date, you can use the origin and end property
    for the purpose.

    >>> imputer8 = TimeSeriesImputer(input_column=['sales'], option='fillna',
    ...                              value=0, origin='2016-12-28')
    >>> imputer8.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2016-12-28    NaN    0.0     a
    1  2016-12-29    NaN    0.0     a
    2  2016-12-30    NaN    0.0     a
    3  2016-12-31    NaN    0.0     a
    4  2017-01-01    NaN    0.0     a
    5  2017-01-02    NaN    1.0     a
    6  2017-01-03    NaN    0.0     a
    7  2017-01-04    3.0    0.0     a
    8  2016-12-28    NaN    0.0     b
    9  2016-12-29    NaN    0.0     b
    10 2016-12-30    NaN    0.0     b
    11 2016-12-31    NaN    0.0     b
    12 2017-01-01    NaN    2.0     b
    13 2017-01-02    4.0    0.0     b
    14 2016-12-28    NaN    0.0     c
    15 2016-12-29    NaN    0.0     c
    16 2016-12-30    NaN    0.0     c
    17 2016-12-31    NaN    0.0     c
    18 2017-01-01    3.0    6.0     c
    19 2017-01-02    6.0    7.0     c
    20 2017-01-03    NaN    0.0     c
    21 2016-12-28    NaN    0.0     d
    22 2016-12-29    NaN    0.0     d
    23 2016-12-30    NaN    0.0     d
    24 2016-12-31    NaN    0.0     d
    25 2017-01-01    2.0   10.0     d
    26 2017-01-02    6.0   11.0     d
    27 2017-01-03    3.0   15.0     d
    28 2017-01-04    5.0   13.0     d
    29 2017-01-05    5.0   14.0     d
    30 2017-01-06    NaN    0.0     d
    31 2017-01-07    NaN    0.0     d
    32 2017-01-08    6.0   15.0     d

    >>> imputer9 = TimeSeriesImputer(input_column=['sales'], option='fillna',
    ...                              value=0, end='2017-01-10')
    >>> imputer9.transform(df1)
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.
    expect 1 distinct datetime frequency from all ['store'] in the data,
    with 2 distinct datetime frequencies (['2D' 'D']) inferred.

    >>>      date  price  sales store
    0  2017-01-02    NaN    1.0     a
    1  2017-01-03    NaN    0.0     a
    2  2017-01-04    3.0    0.0     a
    3  2017-01-05    NaN    0.0     a
    4  2017-01-06    NaN    0.0     a
    5  2017-01-07    NaN    0.0     a
    6  2017-01-08    NaN    0.0     a
    7  2017-01-09    NaN    0.0     a
    8  2017-01-10    NaN    0.0     a
    9  2017-01-01    NaN    2.0     b
    10 2017-01-02    4.0    0.0     b
    11 2017-01-03    NaN    0.0     b
    12 2017-01-04    NaN    0.0     b
    13 2017-01-05    NaN    0.0     b
    14 2017-01-06    NaN    0.0     b
    15 2017-01-07    NaN    0.0     b
    16 2017-01-08    NaN    0.0     b
    17 2017-01-09    NaN    0.0     b
    18 2017-01-10    NaN    0.0     b
    19 2017-01-01    3.0    6.0     c
    20 2017-01-02    6.0    7.0     c
    21 2017-01-03    NaN    0.0     c
    22 2017-01-04    NaN    0.0     c
    23 2017-01-05    NaN    0.0     c
    24 2017-01-06    NaN    0.0     c
    25 2017-01-07    NaN    0.0     c
    26 2017-01-08    NaN    0.0     c
    27 2017-01-09    NaN    0.0     c
    28 2017-01-10    NaN    0.0     c
    29 2017-01-01    2.0   10.0     d
    30 2017-01-02    6.0   11.0     d
    31 2017-01-03    3.0   15.0     d
    32 2017-01-04    5.0   13.0     d
    33 2017-01-05    5.0   14.0     d
    34 2017-01-06    NaN    0.0     d
    35 2017-01-07    NaN    0.0     d
    36 2017-01-08    6.0   15.0     d
    37 2017-01-09    NaN    0.0     d
    38 2017-01-10    NaN    0.0     d

    The imputer works not only for TimeSeriesDataFrame with time_index
    column of type DatetimeIndex, but also TimeSeriesDataFrame with
    time_index column of PeriodIndex as well.

    >>> data2 = pd.DataFrame(
    ...   {'store': ['a', 'a', 'a', 'b', 'b'],
    ...    'brand': ['a', 'a', 'a', 'b', 'b'],
    ...    'date': pd.PeriodIndex(
    ...      ['2011-12', '2012-02', '2012-03', '2012-02', '2012-03'],
    ...      dtype = 'period[M]', freq = 'M'),
    ...    'sales': [1, np.nan, 5, 2, np.nan],
    ...    'price': [np.nan, 2, 3, np.nan, 4]})
    >>> df2 = TimeSeriesDataFrame(data2, grain_colnames=['store', 'brand'],
    ...                          time_colname='date', ts_value_colname='sales')
    >>> df2
      brand    date  price  sales store
    0     a 2011-12    NaN    1.0     a
    1     a 2012-02    2.0    NaN     a
    2     a 2012-03    3.0    5.0     a
    3     b 2012-02    NaN    2.0     b
    4     b 2012-03    4.0    NaN     b
    >>> imputer10 = TimeSeriesImputer(input_column=['sales'],
    ...                               option='fillna', value=0)
    >>> imputer10.transform(df2)
      brand    date  price  sales store
    0     a 2011-12    NaN    1.0     a
    1     a 2012-01    NaN    0.0     a
    2     a 2012-02    2.0    0.0     a
    3     a 2012-03    3.0    5.0     a
    4     b 2012-02    NaN    2.0     b
    5     b 2012-03    4.0    0.0     b

    """

    FFILL_METHOD_STR = 'ffill'

    def __init__(self, input_column,
                 option='fillna', method=None, value=None, limit=None,
                 limit_direction='forward', order=None, freq=None,
                 origin=None, end=None, impute_by_horizon=False):
        """Create a TimeSeriesImputer."""
        self.input_column = input_column
        self.option = option
        self.method = method
        self.value = value
        self.limit = limit
        self.limit_direction = limit_direction
        self.order = order
        if isinstance(freq, str):
            try:
                self.freq = to_offset(freq)     # type: Optional[pd.DateOffset]
            except ValueError:
                # Complex frequencies, set it to None and let it be inferred.
                self.freq = None
        else:
            self.freq = freq
        self.origin = origin
        self.end = end
        self.impute_by_horizon = impute_by_horizon
        self._known_df = None

        # Feature flag for doing dateime gap filling externally in a DatetimeGapFiller transform
        # This flag is used to preserve compatibility between SDK releases
        self._external_datetime_gap_filler = True

    def _get_imports(self):
        return [
            _codegen_utilities.get_import(OrderedDict)
        ]

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params['freq'] = self.freq.freqstr if self.freq is not None else None
        return params

    @classmethod
    def _impute_with_interpolation_single_group(cls, single_group_data,
                                                **kwargs):
        """
        Impute missing values for all columns which contains single group data.

        Uses pandas.DataFrame.interpolate.
        """
        # Need to reset the index for pd.DataFrame.interpolate
        # since only method=linear works when the Series has a multi-index
        interpolation_df = pd.DataFrame(single_group_data).reset_index(
            drop=True)
        interpolation_df = interpolation_df.interpolate(**kwargs)

        # get the index back
        interpolation_df.index = single_group_data.index

        return interpolation_df

    @classmethod
    def _impute_with_fillna_single_group(cls, single_group_data, **kwargs):
        """
        Impute missing values for all columns which contains single group data.

        Uses pandas.DataFrame.fillna.
        """
        method_ = kwargs.get('method')
        value_ = kwargs.get('value')

        if method_ is not None:
            if isinstance(method_, str):
                single_group_data = single_group_data.fillna(method=method_)
            elif isinstance(method_, dict):
                for tmp_method in method_.keys():
                    col_ = method_.get(tmp_method)
                    single_group_data[col_] = single_group_data[col_].fillna(method=tmp_method)
            else:
                raise ClientException('please provide the supported method argument.', has_pii=False,
                                      reference_code=ReferenceCodes._TS_IMPUTER_INVALID_METHOD)

        if value_ is not None:
            single_group_data = single_group_data.fillna(value=value_)

        return single_group_data

    @classmethod
    def _impute_missing_value_by_cols(
            cls, input_df, input_column, sort_index_by_col, by_cols=None,
            option='interpolate', freq=None, origin=None, end=None,
            external_datetime_gap_filler=False, **kwargs):
        """Impute missing value within each group, where groups are defined by by_cols."""

        # Need this block to ensure SDK version compat
        if external_datetime_gap_filler:
            input_df_filled = input_df.sort_index(level=sort_index_by_col)
        else:
            input_df_filled = (input_df.sort_index(level=sort_index_by_col)
                               .fill_datetime_gap(freq=freq, origin=origin, end=end))

        if option == 'interpolate':
            if by_cols is None:
                input_df_filled[input_column] = \
                    cls._impute_with_interpolation_single_group(
                        input_df_filled[input_column], **kwargs)
            else:
                input_df_filled[input_column] = input_df_filled.groupby(
                    by=by_cols, group_keys=False)[input_column].apply(
                    lambda x: cls._impute_with_interpolation_single_group(
                        x, **kwargs))
        elif option == 'fillna':
            method_ = kwargs.get('method')
            known_df_ = kwargs.get('known_df')
            time_index = kwargs.get('time_index')
            revert_method_dict = {}  # type: Dict[str, str]
            if isinstance(method_, str):
                revert_method_dict = {col: method_ for col in input_column}
            elif isinstance(method_, dict):
                for method, cols in method_.items():
                    for col in cols:
                        revert_method_dict[col] = method
            for col in TimeSeriesImputer._get_ffill_cols(input_column, method_):
                known_df_col = None if known_df_ is None else known_df_[col]
                input_df_filled[col] = TimeSeriesImputer._fill_first_row_series_if_nan_ffill(
                    revert_method_dict.get(col), input_df_filled[col], known_df_col, time_index, by_cols=by_cols)
            if by_cols is None:
                input_df_filled[input_column] = \
                    cls._impute_with_fillna_single_group(
                        input_df_filled[input_column], **kwargs)
            else:
                input_df_filled[input_column] = input_df_filled.groupby(
                    by=by_cols, group_keys=False)[input_column].apply(
                    lambda x: cls._impute_with_fillna_single_group(x, **kwargs))
        else:
            raise ClientException(
                'Timeseries imputer only support fillna and interpolate.'
                'Please provide either one of them.', has_pii=False,
                reference_code=ReferenceCodes._TS_IMPUTER_INVALID_OPTION)
        return input_df_filled

    @classmethod
    def _check_value_same_by_column(cls, input_df, value_col, by_cols):
        """Check whether the value_col have same value given by_cols."""
        whether_unique = input_df.groupby(by=by_cols).apply(
            lambda x: (len(np.unique(x[value_col].values)) == 1) or np.isnan(
                x[value_col].values).all())
        return whether_unique.values.all()

    @classmethod
    def _condense_values_by_column(cls, input_df, value_cols, by_cols):
        """Condense the value_cols by by_cols."""
        return input_df.groupby(by=by_cols)[value_cols].first()

    @classmethod
    def _join_df_with_multiindex(cls, df, multi_index):
        """
        Get an output data frame with index equal to multi_index and values joined from the df.

        This helper function is created for scenario when you have a df with
        pandas.MultiIndex which are a subset of indexes in multi_index,
        you want to get a output data frame with index equal to multi_index
        and values joined from the df.
        """
        output_df = pd.DataFrame(df)
        on_cols = df.index.names
        output_df = output_df.reset_index()
        index_df = multi_index.to_frame(index=False)
        output_df = index_df.merge(output_df, on=on_cols, how='left')
        output_df = output_df.set_index(multi_index.names)
        return output_df

    @function_debug_log_wrapped(logging.INFO)
    def fit(
            self,
            X: TimeSeriesDataFrame,
            y: Optional[DataSingleColumnInputType] = None
    ) -> 'TimeSeriesImputer':
        """
        Fit will update the _known_df of the transformer.

        This method is just a pass-through.

        :param X: Input tsdf.
        :param y: Ignored.
        :param single_grain_tsdf_list: The list of tsdf contains single grain value.
        :return: self
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.time_series_imputer.TimeSeriesImputer
        """
        # The latest non nan value of each grain will saved in _known_df.
        self._known_df = TimeSeriesImputer._get_known_df(X, self.input_column, self.method)
        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataFrame) -> TimeSeriesDataFrame:
        """
        Perform imputation on requested data frame columns.

        Here is a brief summary how the TimeSeriesImputer works:
            1. When the input TimeSeriesDataFrame has no property `origin_time`:
                The time series values will be imputed within each time series
                from single `grain_colnames`.
            2. When the input TimeSeriesDataFrame has property `origin_time`:
                a) If time series from the same `grain_colnames have the same value
                as long as the values of `time_colname` are the same, the time
                series will be condensed to have no `origin_time_colname`,
                and get imputed in the condensed data frame. And the imputed
                values will be joined back to the original data by
                `grain_colnames` and `time_colname`.
                b) If time series from the same `grain_colnames` have the same
                value as long as the values of `origin_time_colname` are the
                same, the time series will be condensed to have no
                `time_colname`, and get imputed in the condensed data frame. And
                the imputed values will be joined back to the original data by
                `grain_colnames` and `origin_time_colname`.
                c) For time series not falling into either a) or b), they will be
                imputed within sub-time-series from single combination of
                `grain_colnames` and `origin_time_colname` if impute_by_horizon
                is True. Otherwise, it will be imputed within sub-time-series from
                single combination of `grain_colnames` and `horizon`.

        :param X: Data frame to transform
        :type X: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame

        :return: A data frame with imputed column(s)
        :rtype: azureml.automl.runtime.shared.time_series_data_frame.TimeSeriesDataFrame
        """
        if not isinstance(X, TimeSeriesDataFrame):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDf, target='X',
                                    reference_code=ReferenceCodes._TS_IMPUTER_NOT_TSDF)
            )

        if self.option == 'interpolate':
            if not isinstance(self.method, str):
                raise ClientException('The method is not supported.',
                                      has_pii=False,
                                      reference_code=ReferenceCodes._TS_IMPUTER_UNSUPPORTED_METHOD_TYPE)
            kwargs = {'method': self.method, 'limit': self.limit,
                      'limit_direction': self.limit_direction,
                      'order': self.order}
        elif self.option == 'fillna':
            known_df = None
            if hasattr(self, '_known_df'):
                known_df = getattr(self, '_known_df')
            kwargs = {'method': self.method, 'value': self.value,
                      'limit': self.limit, 'known_df': known_df, 'time_index': X.time_colname}
        else:
            msg = 'The imputation option {} is not supported.'
            raise ClientException(
                msg.format(self.option),
                reference_code=ReferenceCodes._TS_IMPUTER_UNSUPPORTED_OPTION_TRANSFORM,
            ).with_generic_msg(msg.format(
                '[Masked]'))

        if self.freq is None:
            freq = X.infer_freq()
            if freq is None:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesTransCannotInferFreq, target='freq',
                                        reference_code=ReferenceCodes._TS_IMPUTER_NO_FREQ)
                )
        else:
            freq = self.freq

        if isinstance(self.input_column, str):
            self.input_column = [self.input_column]

        #   check whether all elements of the list are in X.columns
        for col in self.input_column:
            if col not in X.columns:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(MissingColumnsInData, target='col',
                                        reference_code=ReferenceCodes._TS_IMPUTER_NO_COLUMN,
                                        columns=str(col),
                                        data_object_name='X.columns')
                )
        # use flag presence and value to determine compat behavior
        external_datetime_gap_filler = self._external_datetime_gap_filler \
            if hasattr(self, '_external_datetime_gap_filler') else False

        # end and origin options are deprecated
        if external_datetime_gap_filler:
            # When the datetime filling feature is on, non-None end and origin are error conditions
            Contract.assert_true(self.origin is None, 'Imputer expects origin option is None (obsolete option)',
                                 log_safe=True)
            Contract.assert_true(self.end is None, 'Imputer expects end option is None (obsolete option)',
                                 log_safe=True)
        elif self.origin is not None or self.end is not None:
            # Old paradigm - allow non-None options but print a deprecation warning
            msg = 'Imputer origin and end options are deprecated. ' + \
                'Values for these option other than None will trigger errors in future releases.'
            warn(msg, PendingDeprecationWarning)
            logger.warning(msg)

        if X.origin_time_colname is None:
            # TODO: Fill in the type annotations for this function and remove the cast
            return cast(TimeSeriesDataFrame, self._impute_missing_value_by_cols(
                input_df=X, input_column=self.input_column,
                sort_index_by_col=X.time_colname,
                by_cols=X.grain_colnames, option=self.option, freq=freq,
                origin=self.origin, end=self.end,
                external_datetime_gap_filler=external_datetime_gap_filler, **kwargs))
        else:
            X_copy = cast(TimeSeriesDataFrame, X.copy())
            # To shorten the variable name, in the following code:
            # `got` means grain_and_origin_time
            # `gt` means grain_and_time
            # `ot` means origin_time
            # `t` means time
            cols_same_given_got = []  # type: List[str]
            cols_same_given_gt = []  # type: List[str]
            other_cols = []  # type: List[str]
            for col in self.input_column:
                # check if the column have same value given grain + time
                if self._check_value_same_by_column(
                        input_df=X, value_col=col,
                        by_cols=X.time_and_grain_colnames):
                    cols_same_given_gt += [col]
                # check if the column have same value given grain + origin_time
                elif self._check_value_same_by_column(
                        input_df=X, value_col=col,
                        by_cols=X.slice_key_colnames):
                    cols_same_given_got += [col]
                else:
                    other_cols += [col]

            if len(cols_same_given_gt) > 0:
                # get the condensed data frame which only have grain + time
                gt_condensed_df = self._condense_values_by_column(
                    input_df=X[cols_same_given_gt],
                    value_cols=cols_same_given_gt,
                    by_cols=X.time_and_grain_colnames)
                gt_condensed_df = TimeSeriesDataFrame(
                    gt_condensed_df, time_colname=X.time_colname,
                    grain_colnames=X.grain_colnames)
                # impute missing value
                gt_condensed_df = self._impute_missing_value_by_cols(
                    input_df=gt_condensed_df,
                    input_column=cols_same_given_gt,
                    sort_index_by_col=X.time_colname,
                    by_cols=X.grain_colnames, option=self.option,
                    freq=freq, origin=self.origin, end=self.end,
                    external_datetime_gap_filler=external_datetime_gap_filler, **kwargs)
                # join the condensed data frame back
                X_copy[cols_same_given_gt] = self._join_df_with_multiindex(
                    gt_condensed_df, X.index)

            if len(cols_same_given_got) > 0:
                # get the condensed data frame which only have grain +
                # origin_time
                got_condensed_df = self._condense_values_by_column(
                    input_df=X[cols_same_given_got],
                    value_cols=cols_same_given_got,
                    by_cols=X.slice_key_colnames)
                got_condensed_df = TimeSeriesDataFrame(
                    got_condensed_df, time_colname=X.origin_time_colname,
                    grain_colnames=X.grain_colnames)
                # impute missing value
                got_condensed_df = self._impute_missing_value_by_cols(
                    input_df=got_condensed_df,
                    input_column=cols_same_given_got,
                    sort_index_by_col=X.origin_time_colname,
                    by_cols=X.grain_colnames, option=self.option,
                    freq=freq, origin=self.origin, end=self.end,
                    external_datetime_gap_filler=external_datetime_gap_filler, **kwargs)
                # join the condensed data frame back
                X_copy[cols_same_given_got] = self._join_df_with_multiindex(
                    got_condensed_df, X.index)

            if len(other_cols) > 0:
                if not self.impute_by_horizon:
                    # impute by slice_key_colnames
                    X_copy[other_cols] = self._impute_missing_value_by_cols(
                        input_df=X_copy[other_cols], input_column=other_cols,
                        sort_index_by_col=X.time_colname,
                        by_cols=X.slice_key_colnames, option=self.option,
                        freq=freq, origin=self.origin, end=self.end,
                        external_datetime_gap_filler=external_datetime_gap_filler,
                        **kwargs)
                else:
                    if HORIZON_COLNAME in X_copy.columns:
                        warn(('The column {} will be overwritted to store the '
                              'integer forecasting horizon.').format(
                            HORIZON_COLNAME))
                    X_copy[HORIZON_COLNAME] = get_period_offsets_from_dates(
                        X_copy.index.get_level_values(X_copy.origin_time_colname),
                        X_copy.index.get_level_values(X_copy.time_colname),
                        freq=freq)
                    # impute by grain + horizon
                    if X_copy.grain_colnames is None:
                        grain_and_horizon_colnames = [HORIZON_COLNAME]
                    else:
                        grain_and_horizon_colnames = X_copy.grain_colnames + [
                            HORIZON_COLNAME]

                    X_copy[other_cols] = self._impute_missing_value_by_cols(
                        input_df=X_copy, input_column=other_cols,
                        sort_index_by_col=X.time_colname,
                        by_cols=grain_and_horizon_colnames, option=self.option,
                        freq=freq, origin=self.origin, end=self.end,
                        external_datetime_gap_filler=external_datetime_gap_filler,
                        **kwargs)[other_cols]

            return X_copy

    @staticmethod
    def _is_leading_nan(single_column_tsdf: TimeSeriesDataFrame) -> bool:
        """
        Check whether a tsdf is leading with NaN

        :param single_column_tsdf: The single column tsdf.
        :return: True if first entry is NaN.
        """
        indices = np.where(pd.notna(single_column_tsdf))
        # The output is a tuple of two arrays, where first is the row index and second in the column index.
        return len(indices[0]) == 0 or np.min(indices[0]) != 0

    @staticmethod
    def _fill_first_row_series_if_nan_ffill(
            method: Union[str, Dict[str, List[str]], None],
            single_column_tsdf: pd.Series,
            single_historic_col: pd.Series,
            time_index: Optional[Any],
            by_cols: Optional[List[str]] = None
    ) -> pd.Series:
        """
        Fill first row of the input data by using the given default dict.

        :param method: Impute NaN method.
        :param single_column_tsdf: The tsdf given to do the ffill.
        :param single_historic_col: The tsdf contains the first value of the data.
        :param by_cols: The grain column name.
        :return: The tsdf with first value filled.
        """
        if not isinstance(time_index, str) or \
                not TimeSeriesImputer._is_fill_leading_nan_enabled(method, single_historic_col):
            return single_column_tsdf
        if by_cols is None and not TimeSeriesImputer._is_leading_nan(single_column_tsdf):
            # do nothing if leading nan for single column.
            return single_column_tsdf
        if by_cols is None:
            TimeSeriesImputer._set_leading_nan_for_single_df(
                single_historic_col, single_column_tsdf, time_index, method)
        else:
            # pd.Series.groupby will yield the index name rather than index content as name field when the series is
            # a single row Series and by is a single element list.
            # known_grain_part here is a dict mapping grain content to the corresponding historical pd.Series.
            if single_historic_col.shape[0] == 1:
                known_grain_part = {
                    TimeSeriesImputer._get_first_row_grain_value(single_historic_col, by_cols): single_historic_col}
            else:
                known_grain_part = dict()  # Dict[Tuple[str], pd.Series]
                for name, max_series in single_historic_col.groupby(by=by_cols):
                    if isinstance(name, str):
                        name = tuple([name])
                    known_grain_part[name] = max_series
            # by_cols here is the grain column names and the keys in the known_grain part dict is the content of
            # each grains as tuple. So here we need to first get the grain contents and then find the correspponding
            # pd.Series to do the filling.
            # All the single grain/multi grain scenarios will convert to the no grain scenario in the lambda function.
            single_column_tsdf = single_column_tsdf.groupby(
                by=by_cols, group_keys=True
            ).apply(
                lambda x: TimeSeriesImputer._set_leading_nan_for_single_df(
                    known_grain_part.get(TimeSeriesImputer._get_first_row_grain_value(x, by_cols)),
                    x, time_index, method))
        return single_column_tsdf

    @staticmethod
    def _set_leading_nan_for_single_df(
            single_historic_col: pd.Series,
            single_column_df: pd.Series,
            time_index: str,
            method: Union[str, Dict[str, List[str]], None]
    ) -> pd.Series:
        """
        Set leading nan according to known df.

        :param single_column_df: df needs to change the first value.
        :param single_historic_col: df contains the known value.
        :time_index: The time index name.
        """
        if not TimeSeriesImputer._is_fill_leading_nan_enabled(method, single_historic_col):
            return single_column_df
        if not TimeSeriesImputer._is_leading_nan(single_column_df):
            # do nothing if leading nan for single column.
            return single_column_df
        last_non_nan_idx = TimeSeriesImputer._get_last_non_nan_idx(single_historic_col)
        if last_non_nan_idx is not None:
            datetime_last_found = TimeSeriesImputer._get_datetime_value(
                single_historic_col, time_index, last_non_nan_idx)
            datetime_missing_index = TimeSeriesImputer._get_datetime_value(single_column_df, time_index, 0)
            if datetime_missing_index >= datetime_last_found:
                single_column_df.iloc[0] = single_historic_col.iloc[last_non_nan_idx]
        return single_column_df

    @staticmethod
    def _get_first_row_grain_value(tsdf: pd.DataFrame, by_columns: List[str]) -> Tuple[Any, ...]:
        """
        Get the first row grain values of a tsdf.

        :param tsdf: Timeseries dataframe.
        :return: First row grain values as a tuple.
        """
        return tuple([tsdf.index.get_level_values(by_col)[0] for by_col in by_columns])

    @staticmethod
    def _get_last_non_nan_value(tsdf: TimeSeriesDataFrame, input_col: List[str]) -> pd.DataFrame:
        """
        Get the last_non_nan_value of each grain and return as a new df.

        :param tsdf: The input timeseries dataframe.
        :param input_col: The interested columns.
        :return: The value saved in a new df format.
        """
        if tsdf.grain_colnames is None:
            # For the no grain or single grain_colnames case, there is no need to get the max by grain.
            return TimeSeriesImputer._get_last_non_nan_value_single_grain(tsdf, input_col)
        else:
            df_list = [grain_df for _, grain_df in tsdf.groupby_grain()]
            return TimeSeriesImputer._get_last_non_nan_value_single_grain_list(df_list, input_col)

    @staticmethod
    def _get_last_non_nan_value_single_grain_list(
            tsdf_list: List[TimeSeriesDataFrame],
            input_col: List[str]
    ) -> pd.DataFrame:
        """
        Get the last_non_nan_value of each grain and return as a new df.

        :param tsdf_list: The list input timeseries dataframe.
        :param input_col: The interested columns.
        :return: The value saved in a new df format.
        """
        indices_df_list = [
            TimeSeriesImputer._get_last_non_nan_value_single_grain(tsdf, input_col) for tsdf in tsdf_list]
        return pd.concat(indices_df_list)

    @staticmethod
    def _get_last_non_nan_value_single_grain(
            tsdf: TimeSeriesDataFrame,
            input_col: List[str]
    ) -> pd.DataFrame:
        """
        Get the last_non_nan_value of each grain and return as a new df.

        :param tsdf: Single or non grain tsdf.
        :param input_col: The interested columns.
        :return: The value saved in a new df format.
        """
        # Extract the interested columns.
        tsdf = tsdf[input_col]
        last_non_nan_indices = TimeSeriesImputer._get_last_non_nan_indices(tsdf, input_col)
        return tsdf.iloc[sorted(last_non_nan_indices)]

    @staticmethod
    def _get_last_non_nan_indices(tsdf: TimeSeriesDataFrame, input_col: List[str]) -> Set[int]:
        """
        Get the list of non nan idx of a tsdf if value is available.

        :param tsdf: TimeSeriesDataFrame.
        :param input_col: the input columns.
        :return: The latest non nan indices set.
        """
        # using a set to ensure the row index added is unique
        last_non_nan_indices = set()
        for col in input_col:
            index = TimeSeriesImputer._get_last_non_nan_idx(tsdf[col])
            if index is not None:
                last_non_nan_indices.add(index)
        return last_non_nan_indices

    @staticmethod
    def _get_last_non_nan_idx(single_column_tsdf: TimeSeriesDataFrame) -> Any:
        """
        Get the last non nan idx of TimeSeriesDataFrame. Return None if the index cannot be found

        :param single_column_tsdf: TimeSeriesDataFrame.
        :return: The latest non nan index.
        """
        not_nan_idx = np.where(pd.notna(single_column_tsdf))[0]
        if not_nan_idx.shape[0] == 0:
            return None
        return np.max(not_nan_idx)

    @staticmethod
    def _get_datetime_value(
            single_column_tsdf: TimeSeriesDataFrame,
            date_index_name: str,
            index: int
    ) -> Any:
        """
        Get the datetime value by index.

        :param single_column_tsdf: single column tsdf.
        :param date_index_name: index name.
        :param index: the row index.
        :return: datetime value as np.datetime64.
        """
        return single_column_tsdf.index.get_level_values(date_index_name)[index]

    @staticmethod
    def _is_fill_leading_nan_enabled(
            method: Union[str, Dict[str, List[str]], None],
            known_df: pd.DataFrame,
    ) -> bool:
        """
        Check whether the fill leading nan can be invoked based on current configuration.

        :param method: The str method or method dict.
        :param known_df: The known df that used for the filling of the first value.
        :return: A boolean that tells if the leading nan is enabled.
        """
        method_check = False
        if isinstance(method, str):
            method_check = (method == TimeSeriesImputer.FFILL_METHOD_STR)
        elif isinstance(method, dict):
            method_check = TimeSeriesImputer.FFILL_METHOD_STR in method.keys()
        return known_df is not None and method_check

    @staticmethod
    def _get_ffill_cols(
            input_column: Union[str, List[str]],
            method: Union[str, Dict[str, List[str]], None]
    ) -> List[str]:
        """
        Get a list of column that will do ffill.

        :param input_column: Input column str or list of input columns.
        :param method: Imputation method.
        :return: A list of columns.
        """
        if isinstance(input_column, str):
            input_column_list = [input_column]
        else:
            input_column_list = input_column

        if isinstance(method, str) or method is None:
            return input_column_list if method == TimeSeriesImputer.FFILL_METHOD_STR else []
        else:
            cols = method.get(TimeSeriesImputer.FFILL_METHOD_STR)
            if isinstance(cols, str):
                return [cols]
            else:
                return method.get(TimeSeriesImputer.FFILL_METHOD_STR) or []

    @staticmethod
    def _get_known_df(
            default_tsdf: Union[TimeSeriesDataFrame, None],
            input_column: List[str],
            method: Union[str, Dict[str, List[str]], None]
    ) -> pd.DataFrame:
        """
        Get the known_df based on the input_column and method.

        :param default_tsdf: The tsdf used to get the known df.
        :param input_column: The input_column list.
        :param method: The imputation method
        """
        if default_tsdf is None:
            return None

        ffill_col = TimeSeriesImputer._get_ffill_cols(input_column, method)

        TimeSeriesImputer._validate_default_tsdf(default_tsdf, ffill_col)
        known_df = TimeSeriesImputer._get_last_non_nan_value(default_tsdf, ffill_col)
        known_df.sort_index(inplace=True)
        # The _is_copy property of a dataframe could be weakref here, use deep equals to true to set it to None for
        # pickling purpose.
        known_df = known_df.copy(deep=True)
        return known_df

    @staticmethod
    def _validate_default_tsdf(
            default_tsdf: TimeSeriesDataFrame,
            ffill_col: List[str]
    ) -> None:
        """
        Validate whether default_tsdf can be used to get the known_df value.

        :param default_tsdf: the tsdf.
        :param ffill_col: the columns that will doing ffill on.
        """
        for col in ffill_col:
            if col not in default_tsdf.columns:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(MissingColumnsInData, target='default_tsdf',
                                        reference_code=ReferenceCodes._TS_IMPUTER_INVALID_DEFAULT_TSDF,
                                        columns=str(col),
                                        data_object_name='default_tsdf.columns')
                )

    def __setstate__(self, state):
        super(TimeSeriesImputer, self).__setstate__(state)
        # add known_df for backward compatibility
        if "_known_df" not in state:
            setattr(self, "_known_df", None)
