#  /************** Begin Copyright - Do not add comments here **************
#   * Licensed Materials - Property of IBM
#   *
#   *   OCO Source Materials
#   *
#   *   (C) Copyright IBM Corp. 2020, All Rights Reserved
#   *
#   * The source code for this program is not published or other-
#   * wise divested of its trade secrets, irrespective of what has
#   * been deposited with the U.S. Copyright Office.
#   ***************************** End Copyright ****************************/

import datetime

from py4j.java_collections import ListConverter, MapConverter
from py4j.java_gateway import is_instance_of
from py4j.protocol import Py4JJavaError

from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage
from autoai_ts_libs.deps.tspy.data_structures.io import MultiTimeSeriesWriter
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries
from autoai_ts_libs.deps.tspy.data_structures.transforms import BinaryTransform
from autoai_ts_libs.deps.tspy.data_structures import utils


class MultiTimeSeries:
    """A collection of :class:`.TimeSeries` where each time-series is identified by some key.

    Notes
    -----
    Like time-series, operations performed against a multi-time-series are executed lazily unless specified otherwise

    All transforms against a multi-time-series will be run in parallel across time-series

    There is no assumption that all time-series must be aligned or have like periodicity.

    Examples
    --------
    create a multi-time-series from a dict

    >>> import autoai_ts_libs.deps.tspy
    >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
    >>> ts2 = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(2,4)).add(autoai_ts_libs.deps.tspy.observation(10,1)).result().to_time_series()
    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
    >>> mts
    a time series
    ------------------------------
    TimeStamp: 0     Value: 1
    TimeStamp: 1     Value: 2
    TimeStamp: 2     Value: 3
    b time series
    ------------------------------
    TimeStamp: 2     Value: 4
    TimeStamp: 10     Value: 1

    create a multi-time-series from a pandas dataframe

    >>> import autoai_ts_libs.deps.tspy
    >>> import numpy as np
    >>> import pandas as pd
    >>> header = ['', 'key', 'timestamp', "name", "age"]
    >>> row1 = ['Row1', "a", 1, "josh", 27]
    >>> row2 = ['Row2', "b", 3, "john", 4]
    >>> row3 = ['Row3', "a", 5, "bob", 17]
    >>> data = np.array([header, row1, row2, row3])
    >>> df = pd.DataFrame(data=data[1:, 1:], index=data[1:, 0], columns=data[0, 1:]).astype(dtype={'key': 'object', 'timestamp': 'int64'})
    >>> mts = autoai_ts_libs.deps.tspy.multi_time_series(df, "key", "timestamp")
    >>> mts
    a time series
    ------------------------------
    TimeStamp: 1     Value: {name=josh, age=27}
    TimeStamp: 5     Value: {name=bob, age=17}
    b time series
    ------------------------------
    TimeStamp: 3     Value: {name=john, age=4}
    """

    def __init__(self, tsc, j_mts):
        self._j_mts = j_mts
        self._tsc = tsc

    def __getitem__(self, item):
        return self.get_time_series(item)

    @property
    def keys(self):
        """
        Returns
        -------
        list
            all keys in this multi-time-series
        """
        return [k for k in self._j_mts.getTimeSeriesMap().keySet()]

    def time_series(self, key):
        """
        get a time-series given a key

        Parameters
        ----------
        key : any
            the key associated with a time-series in this multi-time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series associated with this given key
        """
        return self.get_time_series(key)

    def trs(self, key):
        """
        get a time-series time-reference-system given a key

        Parameters
        ----------
        key : any
            the key associated with a time-series in this multi-time-series

        Returns
        -------
        TRS : :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS`
            this time-series time-reference-system
        """

        return self.get_time_series(key).trs

    def _res_mts(self, mts):
        if self._tsc._always_on_cache is True:
            res = mts.cache()
        else:
            res = mts
        return res

    def write(self, start=None, end=None, inclusive=False):
        """
        create a multi-time-series-writer given a range

        Parameters
        ----------
        start : int or datetime, optional
            start of range (inclusive) (default is None)
        end : int or datetime, optional
            end of range (inclusive) (default is None)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.io.MultiTimeSeriesWriter.MultiTimeSeriesWriter`
            a new multi-time-series-writer

        Raises
        --------
        ValueError
            If there is an error in the input arguments
        """
        if start is None and end is None:
            j_writer = self._j_mts.write(inclusive)
        elif start is not None and end is not None:
            j_writer = self._j_mts.write(start, end, inclusive)
        else:
            raise ValueError("start and end must be either both be specified or neither be specified")
        return MultiTimeSeriesWriter(self._tsc, j_writer)

    def map_series(self, func):
        """
        map each :class:`.ObservationCollection` to a new collection of observations

        Parameters
        ----------
        func : func
            function which given a collection of observations, will produce a new collection of observations

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(2,4)).add(autoai_ts_libs.deps.tspy.observation(10,1)).result().to_multi_time_series()
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 2     Value: 4
        TimeStamp: 10     Value: 1

        add one to each value in our multi-time-series

        >>> mts = mts_orig.map_series(lambda s: s.to_multi_time_series().map(lambda x: x + 1).materialize())
        >>> mts
        a time series
        ------------------------------
        TimeStamp: 0     Value: 2
        TimeStamp: 1     Value: 3
        TimeStamp: 2     Value: 4
        b time series
        ------------------------------
        TimeStamp: 2     Value: 5
        TimeStamp: 10     Value: 2
        """
        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.mapSeries(utils.SeriesUnaryMapFunction(self._tsc, func))
        ))

    def map_series_with_key(self, func):
        """
        map each :class:`.ObservationCollection` to a new collection of observations giving access to
        each time-series key

        Parameters
        ----------
        func : func
            function which given a collection of observations and a key, will produce a new collection of observations

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        """
        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.mapSeriesWithKey(utils.SeriesWithKeyUnaryMapfunctionToSeries(self._tsc, func))
        ))

    def map_series_key(self, func):
        """
        map each time-series key to a new key

        Parameters
        ----------
        func : func
            function which given a time-series key, will produce a new time-series key

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        all produced keys must be unique

        """
        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.mapSeriesKey(utils.UnaryMapFunction(self._tsc, func))
        ))

    def map(self, func):
        """
        produce a new multi-time-series where each observation's value in this multi-time-series is mapped to a new
        observation value

        Parameters
        ----------
        func : func
            value mapping function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.map` for usage
        """
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.map(func)
        ))

    def transform(self, *args):
        """produce a new multi-time-series which is the result of performing a transforming over each time-series. A
        transform can be of type unary (one time-series in, one time-series out) or binary (two time-series in, one
        time-series out)

        Parameters
        ----------
        args : :class:`~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform.UnaryTransform` or :class:`~autoai_ts_libs.deps.tspy.data_structures.transforms.BinaryTransform.BinaryTransform`
            the transformation to apply on each time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Raises
        --------
        ValueError
            If there is an error in the input arguments

        Notes
        -----
        transforms can be shape changing (time-series size out does not necessarily equal time-series size in)

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.transform` for usage
        """
        if len(args) == 0:
            raise ValueError("must provide at least one argument")
        elif len(args) == 1:
            return self._res_mts(MultiTimeSeries(self._tsc, self._j_mts.transform(args[0])))
        elif len(args) == 2:
            if type(args[0]) is MultiTimeSeries:
                if issubclass(type(args[1]), BinaryTransform):
                    return self._res_mts(MultiTimeSeries(self._tsc, self._j_mts.transform(
                        args[0]._j_mts,
                        self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                            utils.JavaToPythonBinaryTransformFunction(self._tsc, args[1])
                        )
                    )))
                else:
                    return self._res_mts(MultiTimeSeries(self._tsc, self._j_mts.transform(
                        args[0]._j_mts,
                        args[1]
                    )))
            else:
                if issubclass(type(args[1]), BinaryTransform):
                    return self._res_mts(MultiTimeSeries(self._tsc, self._j_mts.transform(
                        args[0]._j_ts,
                        self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                            utils.JavaToPythonBinaryTransformFunction(self._tsc, args[1])
                        )
                    )))
                else:
                    return self._res_mts(MultiTimeSeries(self._tsc, self._j_mts.transform(
                        args[0]._j_ts,
                        args[1]
                    )))

    def pair_wise_transform(self, binary_transform):
        """produce a new multi-time-series which is the product of performing a pair-wise transform against all
        combination of keys

        Parameters
        ----------
        binary_transform : BinaryTransform
            the binary transform to execute across all pairs in this multi-time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([1.0, -2.0, 3.0, 4.0])
        >>> ts3 = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 4.0])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2, 'c': ts3})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        b time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: -2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        c time series
        ------------------------------
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 4.0

        perform a pair-wise correlation on this multi-time-series (sliding windows of size 3)

        >>> from autoai_ts_libs.deps.tspy.functions import reducers
        >>> mts = mts_orig.segment(3).pair_wise_transform(reducers.correlation())
        >>> mts
        (a, a) time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 1.0
        (a, b) time series
        ------------------------------
        TimeStamp: 0     Value: 0.3973597071195132
        TimeStamp: 1     Value: 0.9332565252573828
        (b, a) time series
        ------------------------------
        TimeStamp: 0     Value: 0.3973597071195132
        TimeStamp: 1     Value: 0.9332565252573828
        (a, c) time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 0.9819805060619657
        (b, b) time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 1.0
        (c, a) time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 0.9819805060619657
        (b, c) time series
        ------------------------------
        TimeStamp: 0     Value: 0.3973597071195132
        TimeStamp: 1     Value: 0.8485552916276634
        (c, b) time series
        ------------------------------
        TimeStamp: 0     Value: 0.3973597071195132
        TimeStamp: 1     Value: 0.8485552916276633
        (c, c) time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 1.0
        """
        if issubclass(type(binary_transform), BinaryTransform):
            return self._res_mts(MultiTimeSeries(
                self._tsc,
                self._j_mts.pairWiseTransform(
                    self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                        utils.JavaToPythonBinaryTransformFunction(self._tsc, binary_transform)
                    )
                )
            ))
        else:
            return self._res_mts(MultiTimeSeries(
                self._tsc,
                self._j_mts.pairWiseTransform(binary_transform)
            ))

    def fillna(self, interpolator, null_value=None):
        """produce a new multi-time-series which is the result of filling all null values.

        Parameters
        ----------
        interpolator : func or interpolator
            the interpolator method to be used when a value is null
        null_value : any, optional
            denotes a null value, for instance if nullValue = NaN, NaN would be filled

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series
        """
        if hasattr(interpolator, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interpolator)

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.fillna(interpolator, null_value)
        ))

    def resample(self, period, interp_func):
        """produce a new multi-time-series by resampling each time-series to a given periodicity

        Parameters
        ----------
        period : int
            the period to resample to
        func : func or interpolator
            the interpolator method to be used when a value doesn't exist at a given time-tick

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.resample` for usage
        """
        if hasattr(interp_func, '__call__'):
            interp_func = utils.Interpolator(self._tsc, interp_func)

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.resampleSeries(
                self._j_mts,
                period,
                interp_func
            )
        ))

    def filter(self, func):
        """produce a new multi-time-series which is the result of filtering by each observation's value given a filter
        function.

        Parameters
        ----------
        func : func
            the filter on observation's value function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.filter` for usage
        """
        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.filter(func)
        ))

    def filter_series_key(self, func):
        """
        filter each time-series by its key

        Parameters
        ----------
        func : func
            function which given a key will produce a boolean denoting whether to keep the time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([1.0, -2.0, 3.0, 4.0])
        >>> ts3 = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 4.0])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2, 'c': ts3})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        b time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: -2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        c time series
        ------------------------------
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 4.0

        filter each series by key != 'a'

        >>> mts = mts_orig.filter_series_key(lambda k: k != 'a')
        >>> mts
        b time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: -2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        c time series
        ------------------------------
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 4.0
        """
        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.filterSeriesKey(utils.FilterFunction(self._tsc, func))
        ))

    def filter_series(self, func):
        """
        filter each time-series by its time-series object

        Parameters
        ----------
        func : func
            function which given a time-series will produce a boolean denoting whether to keep the
            time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([1.0, -2.0, 3.0, 4.0])
        >>> ts3 = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 4.0])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2, 'c': ts3})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        b time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: -2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        c time series
        ------------------------------
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 4.0

        >>> mts = mts_orig.filter_series(lambda s: -2.0 not in [x.value for x in s.materialize()])
        >>> mts
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        c time series
        ------------------------------
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 4.0
        """
        if hasattr(func, '__call__'):
            func = utils.TimeSeriesFilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.filterSeries(func)
        ))

    def segment(self, window, step=1, enforce_bounds=True):
        """produce a new segment-multi-time-series from a performing a sliding-based segmentation over each time-series

        Parameters
        ----------
        window : int
            number of observations per window
        step : int, optional
            step size to slide (default is 1)
        enforce_size : bool, optional
            if true, will require a window to have the given window size number of observations, otherwise windows can
            have less than or equal to the window size number of observations. (default is True)

        Returns
        -------
        see :func:`~:class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries.SegmentMultiTimeSeries`
            a new segment-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.segment` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries import SegmentMultiTimeSeries
        return self._res_mts(SegmentMultiTimeSeries(
            self._tsc,
            self._j_mts.segment(window, step, enforce_bounds)
        ))

    def to_segments(self, segment_transform):
        """produce a new segment-multi-time-series from a segmentation transform

        Parameters
        ----------
        segment_transform : UnaryTransform
            the transform which will result in a time-series of segments

        Returns
        -------
        see :func:`~:class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries.SegmentMultiTimeSeries`
            a new segment-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.to_segments` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries import SegmentMultiTimeSeries
        return self._res_mts(SegmentMultiTimeSeries(
            self._tsc,
            self._j_mts.toSegments(segment_transform)
        ))

    def segment_by_time(self, window, step):
        """produce a new segment-multi-time-series from a performing a time-based segmentation over each time-series

        Parameters
        ----------
        window : int
            time-tick length of window
        step : int
            time-tick length of step

        Returns
        -------
        see :func:`~:class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries.SegmentMultiTimeSeries`
            a new segment-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.segment_by_time` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries import SegmentMultiTimeSeries
        return self._res_mts(SegmentMultiTimeSeries(
            self._tsc,
            self._j_mts.segmentByTime(window, step)
        ))

    def segment_by_anchor(self, func, left_delta, right_delta):
        """produce a new segment-multi-time-series from performing an anchor-based segmentation over each time-series.
        An anchor point is defined as any value that satisfies the filter function. When an anchor point is determined
        the segment is built based on left_delta time ticks to the left of the point and right_delta time ticks to the
        right of the point.

        Parameters
        ----------
        func : func
            the filter anchor point function
        left_delta : int
            left delta time ticks to the left of the anchor point
        right_delta : int
            right delta time ticks to the right of the anchor point
        perc : int, optional
            number between 0 and 1.0 to denote how often to accept the anchor (default is None)

        Returns
        -------
        see :func:`~:class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries.SegmentMultiTimeSeries`
            a new segment-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.segment_by_anchor` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries import SegmentMultiTimeSeries
        return self._res_mts(SegmentMultiTimeSeries(
            self._tsc,
            self._j_mts.segmentByAnchor(utils.FilterFunction(self._tsc, func), left_delta, right_delta)
        ))

    def segment_by_changepoint(self, change_point=None):
        """produce a new segment-multi-time-series from performing a chang-point based segmentation. A change-point can
        be defined as any change in 2 values that results in a true statement.

        Parameters
        ----------
        change_point : func, optional
            a function given a prev/next value to determine if a change exists (default is simple constant change)

        Returns
        -------
        see :func:`~:class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries.SegmentMultiTimeSeries`
            a new segment-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.segment_by_changepoint` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries import SegmentMultiTimeSeries
        if change_point is None:
            return self._res_mts(SegmentMultiTimeSeries(
                self._tsc,
                self._j_mts.segmentByChangePoint()
            ))
        else:
            return self._res_mts(SegmentMultiTimeSeries(
                self._tsc,
                self._j_mts.segmentByChangePoint(utils.BinaryMapFunction(self._tsc, change_point))
            ))

    def segment_by(self, func):
        """produce a new segment-multi-time-series from a performing a group-by operation on each observation's value
        for each time-series

        Parameters
        ----------
        func : func
            value to key function

        Returns
        -------
        see :func:`~:class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries.SegmentMultiTimeSeries`
            a new segment-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.segment_by` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.SegmentMultiTimeSeries import SegmentMultiTimeSeries
        return self._res_mts(SegmentMultiTimeSeries(
            self._tsc,
            self._j_mts.segmentBy(utils.ObservationToKeyUnaryMapFunction(self._tsc, func))
        ))

    def reduce(self, func):
        """reduce each time-series in this multi-time-series to a single value

        Parameters
        ----------
        func : unary reducer or func
            the unary reducer method to be used

        Returns
        -------
        dict
            the output of time-series reduction for each key

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.reduce` for usage
        """
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        return {k: v for k, v in self._j_mts.reduce(func).items()}

    def reduce_range(self, func, start, end, inclusive=False):
        """
        reduce each time-series in this multi-time-series to a single value given a range

        Parameters
        ----------
        func : unary reducer or func
            the unary reducer method to be used
        start : int or datetime
            start of range (inclusive)
        end : int or datetime
            end of range (inclusive)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        dict
            the output of time-series reduction for each key

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([1.0, -2.0, 3.0, 4.0])
        >>> ts3 = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 4.0])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2, 'c': ts3})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        b time series
        ------------------------------
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: -2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        c time series
        ------------------------------
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 4.0

        reduce each time-series to an average from [1,2]

        >>> from autoai_ts_libs.deps.tspy.functions import reducers
        >>> avg_dict = mts_orig.reduce_range(reducers.average(), 1, 2)
        >>> avg_dict
        {'a': 2.5, 'b': 0.5, 'c': 1.5}
        """
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        return {k: v for k, v in self._j_mts.reduceRange(func, start, end, inclusive).items()}

    def inner_align(self, multi_time_series):
        """align two multi-time-series based on a temporal inner join strategy

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            the multi-time-series to align with

        Returns
        -------
        tuple
            aligned multi-time-series

        Notes
        -----
        inner align will align on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.inner_align` for usage
        """
        pair = self._j_mts.innerAlign(multi_time_series._j_mts)

        return (
            self._res_mts(MultiTimeSeries(self._tsc, pair.left())),
            self._res_mts(MultiTimeSeries(self._tsc, pair.right()))
        )

    def inner_join(self, multi_time_series, join_func=None):
        """join two multi-time-series based on a temporal inner join strategy

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the multi-time-series to join with

        join_func : func, optional
            function to join 2 values at a given time-tick. If None given, joined value will be in a list
            (default is None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        inner join will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.inner_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(multi_time_series, "_j_mts") and is_instance_of(self._tsc._gateway, multi_time_series._j_mts,
                                                                   "com.ibm.research.time_series.core.timeseries.MultiTimeSeries"):
            other_ts = multi_time_series._j_mts
        else:
            other_ts = multi_time_series._j_ts

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.innerJoin(other_ts, utils.BinaryMapFunction(self._tsc, join_func))
        ))

    def full_align(self, multi_time_series, left_interp_func=lambda h, f, ts: None,
                          right_interp_func=lambda h, f, ts: None):
        """align two multi-time-series based on a temporal full join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            the time-series to align with

        left_interp_func : func or interpolator, optional
            the left multi-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        right_interp_func : func or interpolator, optional
            the right multi-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned multi-time-series

        Notes
        -----
        full align will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.full_align` for usage
        """

        if hasattr(left_interp_func, '__call__'):
            interpolator_left = utils.Interpolator(self._tsc, left_interp_func)
        else:
            interpolator_left = left_interp_func

        if hasattr(right_interp_func, '__call__'):
            interpolator_right = utils.Interpolator(self._tsc, right_interp_func)
        else:
            interpolator_right = right_interp_func

        pair = self._j_mts.fullAlign(
            multi_time_series._j_mts,
            interpolator_left,
            interpolator_right
        )

        return (
            self._res_mts(MultiTimeSeries(self._tsc, pair.left())),
            self._res_mts(MultiTimeSeries(self._tsc, pair.right()))
        )

    def full_join(self, multi_time_series, join_func=None, left_interp_func=lambda h, f, ts: None,
                         right_interp_func=lambda h, f, ts: None):
        """join two multi-time-series based on a temporal full join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the multi-time-series to join with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        left_interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        right_interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        full join will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.full_join` for usage
        """

        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(left_interp_func, '__call__'):
            interpolator_left = utils.Interpolator(self._tsc, left_interp_func)
        else:
            interpolator_left = left_interp_func

        if hasattr(right_interp_func, '__call__'):
            interpolator_right = utils.Interpolator(self._tsc, right_interp_func)
        else:
            interpolator_right = right_interp_func

        if is_instance_of(self._tsc._gateway, multi_time_series._j_mts,
                          "com.ibm.research.time_series.core.timeseries.MultiTimeSeries"):
            other_ts = multi_time_series._j_mts
        else:
            other_ts = multi_time_series._j_ts

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.fullJoin(
                other_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator_left,
                interpolator_right,
            )
        ))

    def left_align(self, multi_time_series, interp_func=lambda h, f, ts: None):
        """align two multi-time-series based on a temporal left join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            the time-series to align with

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned multi-time-series

        Notes
        -----
        left align will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.left_align` for usage
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_mts.leftAlign(
            multi_time_series._j_mts,
            interpolator
        )

        return (
            self._res_mts(MultiTimeSeries(self._tsc, pair.left())),
            self._res_mts(MultiTimeSeries(self._tsc, pair.right()))
        )

    def left_join(self, multi_time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two multi-time-series based on a temporal left join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the multi-time-series to join with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        left join will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.left_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        if is_instance_of(self._tsc._gateway, multi_time_series._j_mts,
                          "com.ibm.research.time_series.core.timeseries.MultiTimeSeries"):
            other_ts = multi_time_series._j_mts
        else:
            other_ts = multi_time_series._j_ts

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.leftJoin(
                other_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def right_align(self, multi_time_series, interp_func=lambda h, f, ts: None):
        """align two multi-time-series based on a temporal right join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            the time-series to align with

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned multi-time-series

        Notes
        -----
        right align will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.right_align` for usage
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_mts.rightAlign(
            multi_time_series._j_mts,
            interpolator
        )

        return (
            self._res_mts(MultiTimeSeries(self._tsc, pair.left())),
            self._res_mts(MultiTimeSeries(self._tsc, pair.right()))
        )

    def right_join(self, multi_time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two multi-time-series based on a temporal right join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the multi-time-series to join with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        right join will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.right_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        if is_instance_of(self._tsc._gateway, multi_time_series._j_mts,
                          "com.ibm.research.time_series.core.timeseries.MultiTimeSeries"):
            other_ts = multi_time_series._j_mts
        else:
            other_ts = multi_time_series._j_ts

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.rightJoin(
                other_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def left_outer_align(self, multi_time_series, interp_func=lambda h, f, ts: None):
        """align two multi-time-series based on a temporal left outer join strategy and optionally interpolate missing
        values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            the multi-time-series to align with

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned multi-time-series

        Notes
        -----
        left outer align will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.left_outer_align` for usage
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_mts.leftOuterAlign(
            multi_time_series._j_mts,
            interpolator
        )

        return (
            self._res_mts(MultiTimeSeries(self._tsc, pair.left())),
            self._res_mts(MultiTimeSeries(self._tsc, pair.right()))
        )

    def left_outer_join(self, multi_time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two multi-time-series based on a temporal left outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the multi-time-series to join with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        left outer join will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.left_outer_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        if is_instance_of(self._tsc._gateway, multi_time_series._j_mts,
                          "com.ibm.research.time_series.core.timeseries.MultiTimeSeries"):
            other_ts = multi_time_series._j_mts
        else:
            other_ts = multi_time_series._j_ts

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.leftOuterJoin(
                other_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def right_outer_align(self, multi_time_series, interp_func=lambda h, f, ts: None):
        """align two time-series based on a temporal right outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            the multi-time-series to align with

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned multi-time-series

        Notes
        -----
        right outer align will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.right_outer_align` for usage
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_mts.rightOuterAlign(
            multi_time_series._j_mts,
            interpolator
        )

        return (
            self._res_mts(MultiTimeSeries(self._tsc, pair.left())),
            self._res_mts(MultiTimeSeries(self._tsc, pair.right()))
        )

    def right_outer_join(self, multi_time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two multi-time-series based on a temporal right outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        multi_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries` or :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the multi-time-series to join with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        right outer join will join on like time-series keys. If a key does not exist in one time-series, it will be
        discarded

        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.right_outer_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        if is_instance_of(self._tsc._gateway, multi_time_series._j_mts,
                          "com.ibm.research.time_series.core.timeseries.MultiTimeSeries"):
            other_ts = multi_time_series._j_mts
        else:
            other_ts = multi_time_series._j_ts

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.rightOuterJoin(
                other_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def align(self, key, interp_func=lambda h, f, ts: None):
        """
        align all time-series on a key

        Parameters
        ----------
        key : any
            key to a time-series within this multi-time-series
        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(2,4)).add(autoai_ts_libs.deps.tspy.observation(10,1)).result().to_multi_time_series()
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 2     Value: 4
        TimeStamp: 10     Value: 1

        align all time-series on time-series 'b'

        >>> mts = mts_orig.align("b")
        >>> mts
        a time series
        ------------------------------
        TimeStamp: 2     Value: 3
        TimeStamp: 10     Value: null
        b time series
        ------------------------------
        TimeStamp: 2     Value: 4
        TimeStamp: 10     Value: 1
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return self._res_mts(MultiTimeSeries(
            self._tsc,
            self._j_mts.align(
                key,
                interpolator
            )
        ))

    def forecast(self, num_predictions, fm, start_training_time=None, confidence=None):
        """forecast the next num_predictions using a forecasting model for each time-series

        Parameters
        ----------
        num_predictions : int
            number of forecasts past the end of the time-series to retrieve
        fm : :class:`~autoai_ts_libs.deps.tspy.data_structures.forecasting.ForecastingModel.ForecastingModel`
            the forecasting model to use
        start_training_time : int or datetime, optional
            point at which to start training the forecasting model
        confidence : float
            number between 0 and 1 which is used in calculating the confidence interval

        Returns
        -------
        dict
            a collection of observations for each key

        Raises
        --------
        TSErrorWithMessage
            If there is an error in forecasting

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.forecast` for usage
        """
        from autoai_ts_libs.deps.tspy.data_structures.forecasting import ForecastingModel
        if isinstance(fm, dict):
            j_fm = {}
            for k, v in fm.items():
                if isinstance(fm, ForecastingModel.ForecastingModel):
                    j_fm[k] = self._tsc._jvm.com.ibm.research.time_series.transforms.forecastors.Forecasters.general(v._j_fm)
                else:
                    j_fm[k] = fm
            j_fm = MapConverter().convert(j_fm, self._tsc._gateway._gateway_client)
        else:
            if isinstance(fm, ForecastingModel.ForecastingModel):
                j_fm = self._tsc._jvm.com.ibm.research.time_series.transforms.forecastors.Forecasters.general(fm._j_fm)
            else:
                j_fm = fm

        try:
            if start_training_time is None:
                j_map = self._j_mts.forecast(num_predictions, j_fm,  1.0 if confidence is None else confidence)
            else:
                if isinstance(start_training_time, datetime.datetime):
                    if start_training_time.tzinfo is None or start_training_time.tzinfo.utcoffset(
                            start_training_time) is None:  # this is a naive datetime, must make it aware
                        start = start_training_time.replace(tzinfo=datetime.timezone.utc)

                    j_start = self._tsc._jvm.java.time.ZonedDateTime.parse(
                        str(start.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                        self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
                    )
                else:
                    j_start = start_training_time

                j_map = self._j_mts.forecast(num_predictions, j_fm, j_start,  1.0 if confidence is None else confidence)

            result = {}
            from autoai_ts_libs.deps.tspy.data_structures import Prediction
            if confidence is None:
                for k, j_observations in j_map.items():
                    py_ts_builder = self._tsc.observations.builder()
                    for j_obs in j_observations.iterator():
                        py_ts_builder.add((j_obs.getTimeTick(), Prediction(self._tsc, j_obs.getValue()).value))
                    result[k] = py_ts_builder.result()
            else:
                for k, j_observations in j_map.items():
                    py_ts_builder = self._tsc.observations.builder()
                    for j_obs in j_observations.iterator():
                        py_ts_builder.add((j_obs.getTimeTick(), Prediction(self._tsc, j_obs.getValue())))
                    result[k] = py_ts_builder.result()

            return result

        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            msg = "There was an issue forecasting, this may be caused by incorrect types given to chained operations"
            raise TSErrorWithMessage(msg)

    def describe(self):
        """retrieve a :class:`~autoai_ts_libs.deps.tspy.data_structures.NumStats` object per time-series computed from all values in this
        multi-time-series (double)

        Returns
        -------
        dict
            :class:`~autoai_ts_libs.deps.tspy.data_structures.NumStats` for each key

        Raises
        --------
        TSErrorWithMessage
            `describe` doesn't work with the data type

        """
        collected = self.collect_as_map()
        type_determined = ""
        for k, v in collected.items():
            if not v.is_empty():
                type_determined = type(v.first().value)

        if type_determined is float or type_determined is int:
            from autoai_ts_libs.deps.tspy.data_structures.NumStats import NumStats
            j_map_stats = self._j_mts.reduce(
                self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.describeNumeric()
            )
            py_map_stats = {}
            for k, v in j_map_stats.items():
                py_map_stats[k] = NumStats(self._tsc, v)
        else:
            # from autoai_ts_libs.deps.tspy.data_structures.Stats import Stats
            # j_map_stats = self._j_mts.reduceSeries(
            #     self._tsc._jvm.com.ibm.research.data_structures.core.core_transforms.general.GeneralReducers.describe()
            # )
            # py_map_stats = {}
            # for k, v in j_map_stats.items():
            #     py_map_stats[k] = Stats(self._tsc, v)
            raise TSErrorWithMessage("describe for non-float / int values is not yet supported")
        return py_map_stats

    def cache(self, cache_size=None):
        """suggest to the multi-time-series to cache values

        Parameters
        ----------
        cache_size : int, optional
            the max cache size (default is max long)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series

        Notes
        -----
        this is a lazy operation and will only suggest to the multi-time-series to save values once computed
        """
        if cache_size is None:
            self._j_mts.cache()
        else:
            self._j_mts.cache(cache_size)
        return self

    def uncache(self):
        """remove the multi-time-series caching mechanism

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series
        """
        self._j_mts.uncache()
        return self

    def with_trs(self, granularity=datetime.timedelta(milliseconds=1), time_tick=datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)):
        """create a new multi-time-series with its timestamps mapped based on a granularity and start_time. In the
        scope of this method, granularity refers to the granularity at which to see time_ticks and start_time refers to
        the zone-date-time in which to start your time-series data when calling
        :func:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries.materialize`

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is 1ms)
        start_time : datetime, optional
            the starting date-time of the time-series (default is 1970-01-01 UTC)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a new multi-time-series with its time_ticks mapped based on a new :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS`.

        Notes
        -----
        time_ticks will be mapped as follows - (current_time_tick - start_time) / granularity

        if any source time-series does not have a time-reference-system associated with it, this method will
        throw and exception
        """
        j_time_tick = self._tsc._jvm.java.time.Duration.ofMillis(
            int(((granularity.microseconds + (
                    granularity.seconds + granularity.days * 24 * 3600) * 10 ** 6) / 10 ** 6) * 1000)
        )

        if time_tick.tzinfo is None or time_tick.tzinfo.utcoffset(time_tick) is None: # this is a naive datetime, must make it aware
            import datetime
            time_tick = time_tick.replace(tzinfo=datetime.timezone.utc)


        j_zdt = self._tsc._jvm.java.time.ZonedDateTime.parse(
            str(time_tick.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
            self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
        )

        j_trs = self._tsc._jvm.com.ibm.research.time_series.core.utils.TRS.of(j_time_tick, j_zdt)

        return self._res_mts(
            MultiTimeSeries(
                self._tsc,
                self._j_mts.withTRS(j_trs)
            )
        )

    def aggregate(self, zero, seq_func, comb_func):
        """
        aggregate all series in this multi-time-series to produce a single value

        Parameters
        ----------
        zero : any
            zero value for aggregation
        seq_func : func
            operation to perform against each time series to reduce a time series to a single value
        comb_func : func
            operation to perform against each reduced time series values to combine those values

        Returns
        -------
        any
             single output value representing the aggregate of all time-series in the multi-time-series

        Raises
        --------
        TSErrorWithMessage
            If there is an error in aggregating, e.g. incorrect type

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(2,4)).add(autoai_ts_libs.deps.tspy.observation(10,1)).result().to_multi_time_series()
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        >>> mts_orig
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 2     Value: 4
        TimeStamp: 10     Value: 1

        get the sum over all time-series

        >>> from autoai_ts_libs.deps.tspy.functions import reducers
        >>> sum = mts_orig.aggregate(0, lambda agg,cur: agg + cur.reduce(reducers.sum()), lambda agg1, agg2: agg1 + agg2)
        >>> sum
        11.0
        """
        try:
            return self._j_mts.aggregate(
                zero,
                utils.ValueAndTimeSeriesBinaryMapFunction(self._tsc, seq_func),
                utils.BinaryMapFunction(self._tsc, comb_func)
            )
        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            msg = "There was an issue aggregating, this may be caused by incorrect types given to chained operations"
            raise TSErrorWithMessage(msg)

    def aggregate_series(self, list_to_val_func):
        """
        aggregate all time-series in the multi-time-series using a summation function to produce a single time-series

        Parameters
        ----------
        list_to_val_func : func
            function which produces a single value given a list of values

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Notes
        -----
        all time-series in this multi-time-series should be aligned prior to calling aggregate_series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([2,3,4])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 0     Value: 2
        TimeStamp: 1     Value: 3
        TimeStamp: 2     Value: 4

        create a sum per time-tick time-series

        >>> ts = mts_orig.aggregate_series(lambda l: sum(l))
        TimeStamp: 0     Value: 3
        TimeStamp: 1     Value: 5
        TimeStamp: 2     Value: 7
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
        j_ts = self._j_mts.aggregateSeries(utils.NaryMapFunction(self._tsc, list_to_val_func))
        return TimeSeries(
            self._tsc,
            j_ts
        )

    def aggregate_series_with_key(self, list_to_val_func):
        """
        aggregate all time-series with key in the multi-time-series using a summation function to produce a single
        time-series

        Parameters
        ----------
        list_to_val_func : func
            function which produces a single value given a list of pairs with key and value

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
        j_ts = self._j_mts.aggregateSeriesWithKey(utils.UnaryListPairMapFunction(self._tsc, list_to_val_func))
        return TimeSeries(
            self._tsc,
            j_ts
        )

    def get_time_series(self, key):
        """
        get a time-series given a key

        Parameters
        ----------
        key : any
            the key associated with a time-series in this multi-time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series associated with the given key

        Raises
        --------
        ValueError
            If there is an error in aggregating, e.g. incorrect key
        """
        try:
            from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries

            j_ts = self._j_mts.getTimeSeriesMap().get(key)

            if j_ts.getTRS() is None:
                return TimeSeries(self._tsc, j_ts)
            else:
                from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
                j_trs = j_ts.getTRS()
                time_tick = datetime.timedelta(milliseconds=j_trs.getTimeTick().toMillis())
                offset = datetime.datetime.strptime(
                    j_trs.getOffset().format(self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX]")),
                    "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                return TimeSeries(self._tsc, j_ts, TRS(self._tsc, time_tick, offset, j_trs))

        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            msg = "There was an issue getting a time-series, please make sure the given key exists in your MultiTimeSeries"
            raise ValueError(msg)

    def collect_series(self, key, inclusive=False):
        """
        get a collection of observations given a key

        Parameters
        ----------
        key : any
            the key associated with a time-series in this multi-time-series
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        :class:`.ObservationCollection`
            the collection of observations associated with the given key

        Raises
        --------
        ValueError
            If there is an error in aggregating, e.g. incorrect key
        """
        try:
            return self.get_time_series(key).materialize(inclusive)
        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            raise ValueError("There was an issue getting an ObservationCollection, please make sure the given key "
                              "exists in your MultiTimeSeries")

    def get_values(self, start, end, inclusive=False):
        return self.materialize(start, end, inclusive)

    def collect(self, inclusive=False):
        return self.materialize(inclusive=inclusive)

    def materialize(self, start=None, end=None, inclusive=False):
        """get all values between a range in this multi-time-series

        Parameters
        ----------
        start : int or datetime
            start of range (inclusive)
        end : int or datetime
            end of range (inclusive)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        :class:`.BoundMultiTimeSeries`
            a collection of observations for each key

        Raises
        --------
        TSErrorWithMessage
            If there is an error in collecting data, e.g. incorrect type

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries.materialize` for usage
        """
        if start is None and end is None:
            try:
                j_map = self._j_mts.materialize(inclusive)
                from autoai_ts_libs.deps.tspy.data_structures.observations.BoundMultiTimeSeries import BoundMultiTimeSeries
                return BoundMultiTimeSeries(self._tsc, j_map)
            except(Py4JJavaError):
                if self._tsc._kill_gateway_on_exception:
                    self._tsc._gateway.shutdown()
                raise TSErrorWithMessage(
                    "There was an issue collecting data, this may be caused by incorrect types given to "
                    "chained operations")
        elif start is None or end is None:
            raise TSErrorWithMessage("start and end must be none or specified")
        else:
            try:
                if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
                    if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:  # this is a naive datetime, must make it aware
                        start = start.replace(tzinfo=datetime.timezone.utc)
                    if end.tzinfo is None or end.tzinfo.utcoffset(end) is None:  # this is a naive datetime, must make it aware
                        end = end.replace(tzinfo=datetime.timezone.utc)

                    j_zdt_start = self._tsc._jvm.java.time.ZonedDateTime.parse(
                        str(start.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                        self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
                    )

                    j_zdt_end = self._tsc._jvm.java.time.ZonedDateTime.parse(
                        str(end.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                        self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
                    )
                    j_map = self._j_mts.materialize(j_zdt_start, j_zdt_end, inclusive)
                    from autoai_ts_libs.deps.tspy.data_structures.observations.BoundMultiTimeSeries import BoundMultiTimeSeries
                    return BoundMultiTimeSeries(self._tsc, j_map)
                else:
                    j_map = self._j_mts.materialize(start, end, inclusive)
                    from autoai_ts_libs.deps.tspy.data_structures.observations.BoundMultiTimeSeries import BoundMultiTimeSeries
                    return BoundMultiTimeSeries(self._tsc, j_map)
            except(Py4JJavaError):
                if self._tsc._kill_gateway_on_exception:
                    self._tsc._gateway.shutdown()
                raise TSErrorWithMessage("There was an issue collecting data, this may be caused by incorrect types given to "
                                  "chained operations")

    def to_df(self, format="observations", inclusive=False):
        """convert this multi-time-series to a pandas dataframe. A pandas dataframe can wither be stored in observations
        format (key column per row) or instants format (one time-series per column)

        Parameters
        ----------
        format : str, optional
            dataframe format to store in (default is observations format)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        dataframe
            a pandas dataframe representation of this time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([2,3,4])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 0     Value: 2
        TimeStamp: 1     Value: 3
        TimeStamp: 2     Value: 4

        create an observations dataframe

        >>> df = mts_orig.to_df(format="observations")
        >>> df
           timestamp key  value
        0          0   a      1
        1          1   a      2
        2          2   a      3
        3          0   b      2
        4          1   b      3
        5          2   b      4

        create an instants dataframe

        >>> mts = mts_orig.to_df(format="instants")
        >>> mts
           timestamp  a  b
        0          0  1  2
        1          1  2  3
        2          2  3  4
        """
        if format == "observations":
            return self.to_df_observations(inclusive)
        elif format == "instants":
            return self.to_df_instants(inclusive)
        else:
            raise TSErrorWithMessage("format must be one of observations or instants")

    def to_df_observations(self, inclusive=False):
        """convert this multi-time-series to an observations pandas dataframe. An observations dataframe is one which
        contains a key column per record.

        Parameters
        ----------
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        dataframe
            a pandas dataframe representation of this time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([2,3,4])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 0     Value: 2
        TimeStamp: 1     Value: 3
        TimeStamp: 2     Value: 4

        create an observations dataframe

        >>> df = mts_orig.to_df_observations()
        >>> df
           timestamp key  value
        0          0   a      1
        1          1   a      2
        2          2   a      3
        3          0   b      2
        4          1   b      3
        5          2   b      4
        """
        from io import StringIO
        csv_str = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.saveMultiTimeSeriesAsJsonString(
            self._j_mts,
            inclusive
        )
        import pandas as pd
        return pd.read_json(StringIO(csv_str), orient="records")

    def to_df_instants(self, inclusive=False):
        """convert this multi-time-series to an observations pandas dataframe. An observations dataframe is one which
        contains a time-series per column.

        Parameters
        ----------
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        dataframe
            a pandas dataframe representation of this time-series

        Examples
        --------
        create a simple multi-time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([1,2,3])
        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([2,3,4])
        >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series({'a': ts1, 'b': ts2})
        a time series
        ------------------------------
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        b time series
        ------------------------------
        TimeStamp: 0     Value: 2
        TimeStamp: 1     Value: 3
        TimeStamp: 2     Value: 4

        create an instants dataframe

        >>> mts = mts_orig.to_df_instants()
        >>> mts
           timestamp  a  b
        0          0  1  2
        1          1  2  3
        2          2  3  4
        """
        from io import StringIO
        csv_str = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.saveMultiTimeSeriesInstantsAsJsonString(
            self._j_mts,
            inclusive
        )
        import pandas as pd
        return pd.read_json(StringIO(csv_str))

    def print(self, start=None, end=None, inclusive=False):
        """print this multi-time-series

        Parameters
        ----------
        start : int or datetime, optional
            start of range (inclusive) (default is current first time-tick)
        end : int or datetime
            end of range (inclusive) (default is current last time-tick)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Raises
        --------
        ValueError
            If there is an error in the input arguments.
        """
        if start is None and end is None:
            print(self._j_mts.toString())
        elif start is not None and end is not None:
            if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
                if start.tzinfo is None or start.tzinfo.utcoffset(start) is None:  # this is a naive datetime, must make it aware
                    start = start.replace(tzinfo=datetime.timezone.utc)
                if end.tzinfo is None or end.tzinfo.utcoffset(end) is None:  # this is a naive datetime, must make it aware
                    end = end.replace(tzinfo=datetime.timezone.utc)

                j_zdt_start = self._tsc._jvm.java.time.ZonedDateTime.parse(
                    str(start.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                    self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
                )

                j_zdt_end = self._tsc._jvm.java.time.ZonedDateTime.parse(
                    str(end.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                    self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
                )
                print(self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.multiTimeSeriesToString(self._j_mts, j_zdt_start, j_zdt_end, inclusive))
            else:
                print(self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.multiTimeSeriesToString(self._j_mts, start, end, inclusive))
        else:
            raise ValueError("start and end must both either be set or be None")

    def __str__(self):
        return self._j_mts.toString()

    def __repr__(self):
        return self._j_mts.toString()
