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

from py4j.java_collections import ListConverter
from py4j.protocol import Py4JJavaError

from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage
from autoai_ts_libs.deps.tspy.data_structures.io.TimeSeriesWriter import TimeSeriesWriter
from autoai_ts_libs.deps.tspy.data_structures.observations import BoundTimeSeries
from autoai_ts_libs.deps.tspy.data_structures import utils
from autoai_ts_libs.deps.tspy.data_structures.transforms import UnaryTransform, BinaryTransform
import datetime


class TimeSeries:

    """This is the abstract portrayal of lazily evaluated immutable TimeSeries.
    By lazy, we mean that this time series will only get values when explicitly asked for.
    By immutable, we mean this time series' observations may never be directly mutated.

    A TimeSeries object can either be physical(having a source) or it can be from
    some other TimeSeries. One can think of TimeSeries as a series where each value is an
    Observation in the series. TimeSeries objects have the property where, values are computed lazily
    meaning, execution of a TimeSeries pipeline only continues, when one asks for values

    Attributes
    ----------
    trs: :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS`
        a time-reference-system

    Raises
    --------
    ValueError
        If there is an error in the input arguments

    Examples
    --------
    create a time series from a list

    >>> import autoai_ts_libs.deps.tspy
    >>> autoai_ts_libs.deps.tspy.time_series([1, 2, 3])
    TimeStamp: 0     Value: 1
    TimeStamp: 1     Value: 2
    TimeStamp: 2     Value: 3

    create a time series from a list with a time-reference-system

    >>> import autoai_ts_libs.deps.tspy
    >>> import datetime
    >>> granularity = datetime.timedelta(days=1)
    >>> start_time = datetime.datetime(1990, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
    >>> autoai_ts_libs.deps.tspy.time_series([1, 2, 3], granularity=granularity, start_time=start_time)
    TimeStamp: 1990-01-01T00:00Z     Value: 1
    TimeStamp: 1990-01-02T00:00Z     Value: 2
    TimeStamp: 1990-01-03T00:00Z     Value: 3

    create a time series from a pandas dataframe

    >>> import autoai_ts_libs.deps.tspy
    >>> import numpy as np
    >>> import pandas as pd
    >>> header = ['', 'key', 'timestamp', "name", "age"]
    >>> row1 = ['Row1', "a", 1, "josh", 27]
    >>> row2 = ['Row2', "b", 3, "john", 4]
    >>> row3 = ['Row3', "a", 5, "bob", 17]
    >>> data = np.array([header, row1, row2, row3])
    >>> df = pd.DataFrame(data=data[1:, 1:], index=data[1:, 0], columns=data[0, 1:])
    >>> autoai_ts_libs.deps.tspy.time_series(df, ts_column="timestamp")
    TimeStamp: 1     Value: {name=josh, age=27, key=a}
    TimeStamp: 3     Value: {name=john, age=4, key=b}
    TimeStamp: 5     Value: {name=bob, age=17, key=a}
    """
    def __init__(self, tsc, j_ts, trs=None):
        self._j_ts = j_ts
        self._tsc = tsc
        self._trs = trs

    @property
    def trs(self):
        """
        Returns
        -------
        TRS : :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS`
            this time-series time-reference-system
        """
        return self._trs

    def _res_ts(self, ts, index=None):
        if self._tsc._always_on_cache is True:
            res = ts.cache()
        else:
            res = ts

        if index is not None:
            res._trs = index
        else:
            res._trs = self._trs
        return res

    def write(self, start=None, end=None, inclusive=False):
        """
        create a time-series-writer given a range

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
        :class:`~autoai_ts_libs.deps.tspy.data_structures.io.TimeSeriesWriter.TimeSeriesWriter`
            a new time-series-writer
        """
        if start is None and end is None:
            j_writer = self._j_ts.write(inclusive)
        elif start is not None and end is not None:
            j_writer = self._j_ts.write(start, end, inclusive)
        else:
            raise ValueError("start and end must be either both be specified or neither be specified")
        return TimeSeriesWriter(self._tsc, j_writer)

    def with_trs(self, granularity=datetime.timedelta(milliseconds=1), start_time=datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)):
        """create a new time-series with its timestamps mapped based on a granularity and start_time. In the
        scope of this method, granularity refers to the granularity at which to see time_ticks and start_time refers to
        the zone-date-time in which to start your time-series data when calling
        :func:`~autoai_ts_libs.deps.tspy.data_structures.time_Series.TimeSeries.TimeSeries.materialize`

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is 1ms)
        start_time : datetime, optional
            the starting date-time of the time-series (default is 1970-01-01 UTC)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series with its time_ticks mapped based on a new :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS`

        Notes
        -----
        time_ticks will be mapped as follows - (current_time_tick - start_time) / granularity

        if the source time-series does not have a time-reference-system associated with it, this method will
        throw and exception

        Examples
        ---------
        create a time series with a time-reference-system

        >>> import autoai_ts_libs.deps.tspy
        >>> import datetime
        >>> start_time = datetime.datetime(1990, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        >>> granularity = datetime.timedelta(days=1)
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1, 2, 3, 4, 5], granularity=granularity, start_time=start_time)
        >>> ts_orig
        TimeStamp: 1990-01-01T00:00Z     Value: 1
        TimeStamp: 1990-01-02T00:00Z     Value: 2
        TimeStamp: 1990-01-03T00:00Z     Value: 3
        TimeStamp: 1990-01-04T00:00Z     Value: 4
        TimeStamp: 1990-01-05T00:00Z     Value: 5

        re-map this time-series time-reference-system to a new time-reference-system changing only granularity

        note: because we never set a new start_time, the start_time will default to the epoch start time of 1970-01-01

        >>> ts = ts_orig.with_trs(granularity=datetime.timedelta(days=7))
        >>> ts
        TimeStamp: 1989-12-28T00:00Z[UTC]     Value: 1
        TimeStamp: 1989-12-28T00:00Z[UTC]     Value: 2
        TimeStamp: 1989-12-28T00:00Z[UTC]     Value: 3
        TimeStamp: 1990-01-04T00:00Z[UTC]     Value: 4
        TimeStamp: 1990-01-04T00:00Z[UTC]     Value: 5

        re-map this time-series time-reference-system to a new time-reference-system changing both start_time and
        granularity

        >>> granularity = datetime.timedelta(days=7)
        >>> start_time = datetime.datetime(1990, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)
        >>> ts = ts_orig.with_trs(granularity=datetime.timedelta(days=7), start_time=start_time)
        >>> ts
        TimeStamp: 1990-01-01T00:00Z     Value: 1
        TimeStamp: 1990-01-01T00:00Z     Value: 2
        TimeStamp: 1990-01-01T00:00Z     Value: 3
        TimeStamp: 1990-01-01T00:00Z     Value: 4
        TimeStamp: 1990-01-01T00:00Z     Value: 5
        """
        j_time_tick = self._tsc._jvm.java.time.Duration.ofMillis(
            int(((granularity.microseconds + (granularity.seconds + granularity.days * 24 * 3600) * 10 ** 6) / 10 ** 6) * 1000)
        )

        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(start_time) is None: # this is a naive datetime, must make it aware
            import datetime
            start_time = start_time.replace(tzinfo=datetime.timezone.utc)

        j_zdt = self._tsc._jvm.java.time.ZonedDateTime.parse(
            str(start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
            self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
        )

        j_trs = self._tsc._jvm.com.ibm.research.time_series.core.utils.TRS.of(j_time_tick, j_zdt)

        from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
        trs = TRS(self._tsc, granularity, start_time, j_trs)
        return self._res_ts(TimeSeries(self._tsc, self._j_ts.withTRS(j_trs)), trs)

    def map_observation(self, func):
        """produce a new time-series where each observation is mapped to a new observation

        Parameters
        ----------
        func : func
            observation mapping function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series with its observations re-mapped
        """
        from autoai_ts_libs.deps.tspy.functions import expressions
        return self._res_ts(TimeSeries(self._tsc, self._j_ts.mapObservation(expressions._wrap_object_expression(utils.UnaryMapFunction(self._tsc, func)))))

    def map(self, func):
        """produce a new time-series where each observation's value in this time-series is mapped to a new observation value

        Parameters
        ----------
        func : func
            value mapping function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series with its values re-mapped

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1, 2, 3])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        add one to each value of the time-series and produce a new time-series

        >>> ts = ts_orig.map(lambda x: x + 1)
        >>> ts
        TimeStamp: 0     Value: 2
        TimeStamp: 1     Value: 3
        TimeStamp: 2     Value: 4

        map each value of the time-series to a string and produce a new time-series

        >>> ts = ts_orig.map(lambda x: "value - " + str(x))
        >>> ts
        TimeStamp: 0     Value: value - 1
        TimeStamp: 1     Value: value - 2
        TimeStamp: 2     Value: value - 3

        map each value of the time-series to a string using high performant expressions

        >>> from autoai_ts_libs.deps.tspy.functions import expressions as exp
        >>> ts = ts_orig.map(exp.add(exp.id(), 1))
        TimeStamp: 0     Value: 2.0
        TimeStamp: 1     Value: 3.0
        TimeStamp: 2     Value: 4.0
        """

        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        from autoai_ts_libs.deps.tspy.functions import expressions
        return self._res_ts(TimeSeries(self._tsc, self._j_ts.map(expressions._wrap_object_expression(func))))

    def map_with_index(self, func):
        """produce a new time-series where each observation's value in this time-series is mapped given the old value
        and an index to a new observation value

        Parameters
        ----------
        func : func
            value mapping function which includes an index as input

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series with its values re-mapped

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1, 2, 3])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        add one to each value of the time-series and produce a new time-series

        >>> ts = ts_orig.map_with_index(lambda x, index: str(x) + "-" + str(index))
        >>> ts
        TimeStamp: 0     Value: 1 - 0
        TimeStamp: 1     Value: 2 - 1
        TimeStamp: 2     Value: 3 - 2
        """
        if hasattr(func, '__call__'):
            func = utils.BinaryMapFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toBinaryMapWithIndexFunction(func)

        return self._res_ts(TimeSeries(self._tsc, self._j_ts.mapWithIndex(func)))

    def flatmap(self, func):
        """produce a new time-series where each observation's value in this time-series is mapped to 0 to N new values.

        Parameters
        ----------
        func : func
            value mapping function which returns a list of values

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series with its values flat-mapped

        Notes
        -----
        an observations time-tick will be duplicated if a single value maps to multiple values

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1, 2, 3])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        flat map each time-series observation value by duplicating the value

        >>> ts = ts_orig.flatmap(lambda x: [x, x])
        >>> ts
        TimeStamp: 0     Value: 1
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3
        TimeStamp: 2     Value: 3
        """
        return self._res_ts(TimeSeries(self._tsc, self._j_ts.flatMap(utils.FlatUnaryMapFunction(self._tsc, func))))

    def filter(self, func):
        """produce a new time-series which is the result of filtering by each observation's value given a filter
        function.

        Parameters
        ----------
        func : func
            the filter on observation's value function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1, 2, 3])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        filter the time-series for even numbers

        >>> ts = ts_orig.filter(lambda x: x % 2 == 0)
        >>> ts
        TimeStamp: 1     Value: 2

        filter the time-series for even numbers using high performant expressions

        >>> from autoai_ts_libs.deps.tspy.functions import expressions as exp
        >>> ts = ts_orig.filter(exp.divisible_by(exp.id(), 2))
        >>> ts
        TimeStamp: 1     Value: 2
        """

        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return self._res_ts(TimeSeries(self._tsc, self._j_ts.filter(func)))

    def fillna(self, interpolator, null_value=None):
        """produce a new time-series which is the result of filling all null values.

        Parameters
        ----------
        interpolator : func or interpolator
            the interpolator method to be used when a value is null
        null_value : any, optional
            denotes a null value, for instance if nullValue = NaN, NaN would be filled

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1, None, 3])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: null
        TimeStamp: 2     Value: 3

        fill all Nones with another value using a simple fill interpolator

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = ts_orig.fillna(interpolators.fill(2))
        >>> ts
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        fill all 1s with another value using a simple next interpolator.
        Note: fillna will never choose None values from an interpolator unless explicitly specified

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = ts_orig.fillna(interpolators.next(), 1)
        >>> ts
        TimeStamp: 0     Value: 3
        TimeStamp: 1     Value: null
        TimeStamp: 2     Value: 3
        """
        if hasattr(interpolator, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interpolator)

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.fillna(interpolator, null_value)
        ))

    # todo handle nary
    def transform(self, *args):
        """produce a new time-series which is the result of performing a transforming over the time-series. A transform
        can be of type unary (one time-series in, one time-series out) or binary (two time-series in, one time-series
        out)

        Parameters
        ----------
        args : :class:`~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform.UnaryTransform` or :class:`~autoai_ts_libs.deps.tspy.data_structures.transforms.BinaryTransform.BinaryTransform`
            the transformation to apply on this time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Raises
        --------
        ValueError
            If there is an error in the input arguments.

        Notes
        -----
        transforms can be shape changing (time-series size out does not necessarily equal time-series size in)

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0

        perform a simple difference transform

        >>> from autoai_ts_libs.deps.tspy.functions import transformers
        >>> ts = ts_orig.transform(transformers.difference())
        >>> ts
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 1.0

        perform a binary correlation over a sliding window

        >>> ts1 = autoai_ts_libs.deps.tspy.time_series([float(i) for i in range(0,5)]).segment(4)
        >>> ts1
        TimeStamp: 0     Value: original bounds: (0,3) actual bounds: (0,3) observations: [(0,0.0),(1,1.0),(2,2.0),(3,3.0)]
        TimeStamp: 1     Value: original bounds: (1,4) actual bounds: (1,4) observations: [(1,1.0),(2,2.0),(3,3.0),(4,4.0)]

        >>> ts2 = autoai_ts_libs.deps.tspy.time_series([float(5 - i) for i in range(0,5)]).segment(4)
        >>> ts2
        TimeStamp: 0     Value: original bounds: (0,3) actual bounds: (0,3) observations: [(0,5.0),(1,4.0),(2,3.0),(3,2.0)]
        TimeStamp: 1     Value: original bounds: (1,4) actual bounds: (1,4) observations: [(1,4.0),(2,3.0),(3,2.0),(4,1.0)]

        >>> from autoai_ts_libs.deps.tspy.functions import reducers
        >>> ts_corr_windows = ts1.transform(ts2, reducers.correlation())
        >>> ts_corr_windows
        TimeStamp: 0     Value: -1.0
        TimeStamp: 1     Value: -1.0
        """
        if len(args) == 0:
            raise ValueError("must provide at least one argument")
        elif len(args) == 1:
            if issubclass(type(args[0]), UnaryTransform):
                return self._res_ts(TimeSeries(
                    self._tsc,
                    self._j_ts.transform(
                      self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonUnaryTransform(
                          utils.JavaToPythonUnaryTransformFunction(self._tsc, args[0])
                      )
                    )
                ))
            else:
                return self._res_ts(TimeSeries(self._tsc, self._j_ts.transform(args[0])))
        elif len(args) == 2:
            if issubclass(type(args[1]), BinaryTransform):
                return self._res_ts(TimeSeries(
                    self._tsc,
                    self._j_ts.transform(
                        args[0]._j_ts,
                        self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                            utils.JavaToPythonBinaryTransformFunction(self._tsc, args[1])
                        )
                    )
                ))
            else:
                return self._res_ts(TimeSeries(self._tsc, self._j_ts.transform(args[0]._j_ts, args[1])))

    def concat(self, other_time_series):
        """produce a new time-series which is the result of concatenating two time-series

        Parameters
        ----------
        other_time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to concatenate with

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new TimeSeries

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1.0))\
            .add(autoai_ts_libs.deps.tspy.observation(2,2.0))\
            .result()\
            .to_time_series()
        >>> ts_orig
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0

        >>> ts_orig2 = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(3,3.0))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4.0))\
            .result()\
            .to_time_series()
        >>> ts_orig2
        TimeStamp: 3     Value: 3.0
        TimeStamp: 4     Value: 4.0

        >>> ts_concat = ts_orig.concat(ts_orig2)
        >>> ts_concat
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 3.0
        TimeStamp: 4     Value: 4.0

        """
        return self._res_ts(TimeSeries(self._tsc, self._j_ts.concat(other_time_series._j_ts)))

    def __add__(self, other):
        return self.concat(other)

    def to_segments(self, segment_transform):
        """produce a new segment-time-series from a segmentation transform

        Parameters
        ----------
        segment_transform : UnaryTransform
            the transform which will result in a time-series of segments

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 2.0, 1.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 2.0
        TimeStamp: 4     Value: 1.0

        >>> from autoai_ts_libs.deps.tspy.functions import segmenters
        >>> reg_ts = ts_orig.to_segments(segmenters.regression(.5,1,use_relative=True))
        TimeStamp: 0     Value: --range: (0, 2) --outliers: {}
        TimeStamp: 3     Value: --range: (3, 4) --outliers: {}
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries
        return self._res_ts(SegmentTimeSeries(self._tsc, self._j_ts.toSegments(segment_transform)))

    def segment(self, window, step=1, enforce_size=True):
        """produce a new segment-time-series from a performing a sliding-based segmentation over the time-series

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
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0, 5.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        TimeStamp: 4     Value: 5.0

        segment the time-series with a window=3, step=2

        >>> ts = ts_orig.segment(3,2)
        TimeStamp: 0     Value: original bounds: (0,2) actual bounds: (0,2) observations: [(0,1.0),(1,2.0),(2,3.0)]
        TimeStamp: 2     Value: original bounds: (2,4) actual bounds: (2,4) observations: [(2,3.0),(3,4.0),(4,5.0)]

        segment the time-series with a window=3, step=2, enforce_size=False

        >>> ts = ts_orig.segment(3,2, enforce_size=False)
        TimeStamp: 0     Value: original bounds: (0,2) actual bounds: (0,2) observations: [(0,1.0),(1,2.0),(2,3.0)]
        TimeStamp: 2     Value: original bounds: (2,4) actual bounds: (2,4) observations: [(2,3.0),(3,4.0),(4,5.0)]
        TimeStamp: 4     Value: original bounds: (4,4) actual bounds: (4,4) observations: [(4,5.0)]
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries
        return self._res_ts(SegmentTimeSeries(
            self._tsc,
            self._j_ts.segment(window, step, enforce_size)
        ))

    def segment_by(self, func):
        """produce a new segment-time-series from a performing a group-by operation on each observation's value

        Parameters
        ----------
        func : func
            value to key function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0, 5.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        TimeStamp: 4     Value: 5.0

        segment the time-series by even/odd numbers

        >>> ts = ts_orig.segment_by(lambda x: x % 2 == 0)
        >>> ts
        TimeStamp: 0     Value: original bounds: (0,4) actual bounds: (0,4) observations: [(0,1.0),(2,3.0),(4,5.0)]
        TimeStamp: 1     Value: original bounds: (1,3) actual bounds: (1,3) observations: [(1,2.0),(3,4.0)]
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries
        return self._res_ts(SegmentTimeSeries(
            self._tsc,
            self._j_ts.segmentBy(utils.ObservationToKeyUnaryMapFunction(self._tsc, func))
        ))

    def segment_by_time(self, window, step):
        """produce a new segment-time-series from a performing a time-based segmentation over the time-series

        Parameters
        ----------
        window : int
            time-tick length of window
        step : int
            time-tick length of step

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Examples
        ---------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1.0))\
            .add(autoai_ts_libs.deps.tspy.observation(2,2.0))\
            .add(autoai_ts_libs.deps.tspy.observation(6,6.0))\
            .result()\
            .to_time_series()
        >>> ts_orig
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 6     Value: 6.0

        segment the time-series with a time-window length of 3 and a time-step length of 1

        >>> ts = ts_orig.segment_by_time(3,1)
        >>> ts
        TimeStamp: 1     Value: original bounds: (1,3) actual bounds: (1,2) observations: [(1,1.0),(2,2.0)]
        TimeStamp: 2     Value: original bounds: (2,4) actual bounds: (2,2) observations: [(2,2.0)]
        TimeStamp: 3     Value: this segment is empty
        TimeStamp: 4     Value: original bounds: (4,6) actual bounds: (6,6) observations: [(6,6.0)]
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries
        return self._res_ts(SegmentTimeSeries(
            self._tsc,
            self._j_ts.segmentByTime(window, step)
        ))

    def segment_by_anchor(self, func, left_delta, right_delta, perc=None):
        """produce a new segment-time-series from performing an anchor-based segmentation over the time-series. An
        anchor point is defined as any value that satisfies the filter function. When an anchor point is determined the
        segment is built based on left_delta time ticks to the left of the point and right_delta time ticks to the
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
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0, 4.0, 5.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 3.0
        TimeStamp: 3     Value: 4.0
        TimeStamp: 4     Value: 5.0

        segment the time-series by anchor points (even numbers)

        >>> ts = ts_orig.segment_by_anchor(lambda x: x % 2 == 0, 1, 2)
        >>> ts
        TimeStamp: 1     Value: original bounds: (0,3) actual bounds: (0,3) observations: [(0,1.0),(1,2.0),(2,3.0),(3,4.0)]
        TimeStamp: 3     Value: original bounds: (2,5) actual bounds: (2,4) observations: [(2,3.0),(3,4.0),(4,5.0)]
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries

        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        if perc is None:
            return self._res_ts(SegmentTimeSeries(
                self._tsc,
                self._j_ts.segmentByAnchor(func, left_delta, right_delta)
            ))
        else:
            return self._res_ts(SegmentTimeSeries(
                self._tsc,
                self._j_ts.segmentByAnchor(func, left_delta, right_delta, perc)
            ))

    def segment_by_changepoint(self, change_point=None):
        """produce a new segment-time-series from performing a chang-point based segmentation. A change-point can be
        defined as any change in 2 values that results in a true statement.

        Parameters
        ----------
        change_point : func, optional
            a function given a prev/next value to determine if a change exists (default is simple constant change)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 4.0, 5.0, 6.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1.0
        TimeStamp: 1     Value: 2.0
        TimeStamp: 2     Value: 4.0
        TimeStamp: 3     Value: 5.0
        TimeStamp: 4     Value: 6.0

        segment by a change point where the change point is defined as a greater than 1.0 difference between prev/next
        values

        >>> ts = ts_orig.segment_by_changepoint(lambda p, n: abs(n - p) > 1.0)
        >>> ts
        TimeStamp: 0     Value: original bounds: (0,1) actual bounds: (0,1) observations: [(0,1.0),(1,2.0)]
        TimeStamp: 2     Value: original bounds: (2,4) actual bounds: (2,4) observations: [(2,4.0),(3,5.0),(4,6.0)]

        create a simple time-series of strings

        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series(["a","a","a","b","b","c"])
        >>> ts_orig
        TimeStamp: 0     Value: a
        TimeStamp: 1     Value: a
        TimeStamp: 2     Value: a
        TimeStamp: 3     Value: b
        TimeStamp: 4     Value: b
        TimeStamp: 5     Value: c

        segment by a simple constant based change point

        >>> ts = ts_orig.segment_by_changepoint()
        >>> ts
        TimeStamp: 0     Value: original bounds: (0,2) actual bounds: (0,2) observations: [(0,a),(1,a),(2,a)]
        TimeStamp: 3     Value: original bounds: (3,4) actual bounds: (3,4) observations: [(3,b),(4,b)]
        TimeStamp: 5     Value: original bounds: (5,5) actual bounds: (5,5) observations: [(5,c)]
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries
        if change_point is None:
            return self._res_ts(SegmentTimeSeries(
                self._tsc,
                self._j_ts.segmentByChangePoint()
            ))
        else:
            return self._res_ts(SegmentTimeSeries(
                self._tsc,
                self._j_ts.segmentByChangePoint(utils.BinaryMapFunction(self._tsc, change_point))
            ))

    def segment_by_marker(self, *args, **kwargs):
        """produce a new segment-time-series from performing a marker based segmentation. A marker is defined as any
        value that satisfies a marker function.

        Parameters
        ----------
        start_marker : func
            the marker that denotes the start of a segment in the case of two-marker segments (requires end_marker)
        end_marker : func
            the marker that denotes the end of a segment in the case of two-marker segments (requires start_marker)
        marker : func
            the marker that denotes the end of a segment and the beginning of a new segment in the case of single-marker segments
        start_inclusive : bool, optional
            if true, will include the start marker to the segment (default is True)
        end_inclusive : bool, optional
            if true, will include the end marker to the segment (default is True)
        start_on_first : bool, optional
            if true, will start the segment on the first instance of the start marker before an end marker when using
            two-marker segments (default is False)
        end_on_first : bool
            if true, will end the segment on the first instance of the end marker after a start marker when using
            two-marker segments (default is True)
        requires_start_and_end : bool
            if true, a segment will only be created if encapsulated by 2 markers when using single-marker segments
            (default is False)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries.SegmentTimeSeries`
            a new segment-time-series

        Raises
        --------
        ValueError
            If there is an error in the input arguments

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        >>> ts_orig
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 3.0
        TimeStamp: 4     Value: 4.0
        TimeStamp: 5     Value: 5.0

        segment by an even number marker where start_inclusive=True and end_inclusive=False

        >>> ts = ts_orig.segment_by_marker(marker=lambda x: x % 2 == 0, start_inclusive=True, end_inclusive=False)
        >>> ts
        TimeStamp: 0     Value: original bounds: (0,0) actual bounds: (0,0) observations: [(0,0.0)]
        TimeStamp: 1     Value: original bounds: (1,2) actual bounds: (1,2) observations: [(1,1.0),(2,2.0)]
        TimeStamp: 3     Value: original bounds: (3,4) actual bounds: (3,4) observations: [(3,3.0),(4,4.0)]
        TimeStamp: 5     Value: original bounds: (5,5) actual bounds: (5,5) observations: [(5,5.0)]

        segment by start_marker = even number and not 4, end_marker = divisible by 5 and not 0,
        start_inculsive = end_inclusive = True, start_on_first = False, end_on_first = True

        >>> start_marker = lambda x: x % 2 == 0 and x != 4
        >>> end_marker = lambda x: x % 5 == 0 and x != 0
        >>> ts = ts_orig.segment_by_marker(start_marker=start_marker, end_marker=end_marker, start_inclusive=True, end_inclusive=True, start_on_first=False, end_on_first=True)
        >>> ts
        TimeStamp: 2     Value: original bounds: (2,5) actual bounds: (2,5) observations: [(2,2.0),(3,3.0),(4,4.0),(5,5.0)]
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.SegmentTimeSeries import SegmentTimeSeries

        arg_len = len(args)

        if arg_len != 0 and len(kwargs) != 0:
            raise ValueError("Can only specify args or kwargs")
        if arg_len != 0:

            # this is a bi-marker (2 marker functions)
            if arg_len > 1 and hasattr(args[1], '__call__'):
                start_marker = args[0]
                end_marker = args[1]
                start_inclusive = args[2] if arg_len > 2 else True
                end_inclusive = args[3] if arg_len > 3 else True
                start_on_first = args[4] if arg_len > 4 else False
                end_on_first = args[5] if arg_len > 5 else True

                return self._res_ts(SegmentTimeSeries(
                    self._tsc,
                    self._j_ts.segmentByMarker(
                        utils.FilterFunction(self._tsc, start_marker),
                        utils.FilterFunction(self._tsc, end_marker),
                        start_inclusive,
                        end_inclusive,
                        start_on_first,
                        end_on_first
                    )
                ))
            # this is a single marker
            else:
                marker = args[0]
                start_inclusive = args[1] if arg_len > 1 else True
                end_inclusive = args[2] if arg_len > 2 else True
                requires_start_and_end = args[3] if arg_len > 3 else False

                return self._res_ts(SegmentTimeSeries(
                    self._tsc,
                    self._j_ts.segmentByMarker(
                        utils.FilterFunction(self._tsc, marker),
                        start_inclusive,
                        end_inclusive,
                        requires_start_and_end
                    )
                ))
        else:

            # this is a bi-marker (2 marker functions)
            if "start_marker" in kwargs and "end_marker" in kwargs:
                start_marker = kwargs['start_marker']
                end_marker = kwargs['end_marker']
                start_inclusive = kwargs['start_inclusive'] if 'start_inclusive' in kwargs else True
                end_inclusive = kwargs['end_inclusive'] if 'end_inclusive' in kwargs else True
                start_on_first = kwargs['start_on_first'] if 'start_on_first' in kwargs else False
                end_on_first = kwargs['end_on_first'] if 'end_on_first' in kwargs else True

                return self._res_ts(SegmentTimeSeries(
                    self._tsc,
                    self._j_ts.segmentByMarker(
                        utils.FilterFunction(self._tsc, start_marker),
                        utils.FilterFunction(self._tsc, end_marker),
                        start_inclusive,
                        end_inclusive,
                        start_on_first,
                        end_on_first
                    )
                ))
            elif "marker" in kwargs:
                marker = kwargs['marker']
                start_inclusive = kwargs['start_inclusive'] if 'start_inclusive' in kwargs else True
                end_inclusive = kwargs['end_inclusive'] if 'end_inclusive' in kwargs else True
                requires_start_and_end = kwargs['requires_start_and_end'] if 'requires_start_and_end' in kwargs else False

                return self._res_ts(SegmentTimeSeries(
                    self._tsc,
                    self._j_ts.segmentByMarker(
                        utils.FilterFunction(self._tsc, marker),
                        start_inclusive,
                        end_inclusive,
                        requires_start_and_end
                    )
                ))
            else:
                raise ValueError("kwargs must contain at the very least a 'start_marker' and 'end_marker' OR a 'marker' ")

    def lag(self, lag_amount):
        """produce a new time-series which is a lagged version of the current time-series.

        Parameters
        ----------
        lag_amount : int
            number of time-ticks to lag

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        >>> ts_orig.print(2, 4)
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 3.0
        TimeStamp: 4     Value: 4.0

        lag the time-series by 2 time-ticks

        >>> ts = ts_orig.lag(2)
        >>> ts.print(2, 4)
        TimeStamp: 4     Value: 4.0
        TimeStamp: 5     Value: 5.0
        """
        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.lag(lag_amount)
        ))

    def shift(self, shift_amount, default_value=None):
        """produce a new time-series which is a shifted version of the current time-series.

        Parameters
        ----------
        shift_amount : int
            number of records to shift
        default_value : any, optional
            default value to set for padded observations (default is None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Notes
        -----
        Any extra `~autoai_ts_libs.deps.tspy.data_structures.Observation.Observation` will be padded with the given default value

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
        >>> print(ts_orig)
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 3.0
        TimeStamp: 4     Value: 4.0
        TimeStamp: 5     Value: 5.0

        shift the time-series by 2 records filling padded Observations with -1.0

        >>> ts = ts_orig.shift(2, -1.0)
        >>> ts
        TimeStamp: 0     Value: -1.0
        TimeStamp: 1     Value: -1.0
        TimeStamp: 2     Value: 0.0
        TimeStamp: 3     Value: 1.0
        TimeStamp: 4     Value: 2.0
        TimeStamp: 5     Value: 3.0
        """
        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.shift(shift_amount, default_value)
        ))

    def resample(self, period, func):
        """produce a new time-series by resampling the current time-series to a given periodicity

        Parameters
        ----------
        period : int
            the period to resample to
        func : func or interpolator
            the interpolator method to be used when a value doesn't exist at a given time-tick

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(0,0))\
            .add(autoai_ts_libs.deps.tspy.observation(2,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        TimeStamp: 0     Value: 0
        TimeStamp: 2     Value: 2
        TimeStamp: 4     Value: 4

        resample to a periodicity of 1 and fill missing time-ticks with 0

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts_orig.resample(1, interpolators.fill(0))
        TimeStamp: 0     Value: 0
        TimeStamp: 1     Value: 0
        TimeStamp: 2     Value: 2
        TimeStamp: 3     Value: 0
        TimeStamp: 4     Value: 4
        """
        if hasattr(func, '__call__'):
            func = utils.Interpolator(self._tsc, func)

        return self._res_ts(TimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.resample(
                self._j_ts,
                period,
                func
            )
        ))

    def inner_align(self, time_series):
        """align two time-series based on a temporal inner join strategy

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        Returns
        -------
        tuple
            aligned time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
        ....add(autoai_ts_libs.deps.tspy.observation(1,1))\
        ....add(autoai_ts_libs.deps.tspy.observation(3,3))\
        ....add(autoai_ts_libs.deps.tspy.observation(4,4))\
        ....result()\
        ....to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
        ....add(autoai_ts_libs.deps.tspy.observation(2,1))\
        ....add(autoai_ts_libs.deps.tspy.observation(3,2))\
        ....add(autoai_ts_libs.deps.tspy.observation(4,3))\
        ....add(autoai_ts_libs.deps.tspy.observation(5,4))\
        ....result()\
        ....to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        align the two time-series based on a temporal inner join strategy

        >>> (left, right) = left.inner_align(right)
        >>> left
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> right
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        """
        pair = self._j_ts.innerAlign(time_series._j_ts)

        return (
            self._res_ts(TimeSeries(self._tsc, pair.left())),
            self._res_ts(TimeSeries(self._tsc, pair.right()))
        )

    def inner_join(self, time_series, join_func=None):
        """join two time-series based on a temporal inner join strategy

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to join with

        join_func : func, optional
            function to join 2 values at a given time-tick. If None given, joined value will be in a list
            (default is None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
        ....add(autoai_ts_libs.deps.tspy.observation(1,1))\
        ....add(autoai_ts_libs.deps.tspy.observation(3,3))\
        ....add(autoai_ts_libs.deps.tspy.observation(4,4))\
        ....result()\
        ....to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
        ....add(autoai_ts_libs.deps.tspy.observation(2,1))\
        ....add(autoai_ts_libs.deps.tspy.observation(3,2))\
        ....add(autoai_ts_libs.deps.tspy.observation(4,3))\
        ....add(autoai_ts_libs.deps.tspy.observation(5,4))\
        ....result()\
        ....to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal inner join strategy

        >>> ts = orig_left.inner_join(orig_right)
        >>> ts
        TimeStamp: 3     Value: [3, 2]
        TimeStamp: 4     Value: [4, 3]
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.innerJoin(time_series._j_ts, utils.BinaryMapFunction(self._tsc, join_func))
        ))

    def full_align(self, time_series, left_interp_func=lambda h, f, ts: None, right_interp_func=lambda h, f, ts: None):
        """align two time-series based on a temporal full join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        left_interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        right_interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        align the two time-series based on a temporal full join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> (left, right) = orig_left.full_align(orig_right, interpolators.prev(), interpolators.next())
        >>> left
        TimeStamp: 1     Value: 1
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4
        TimeStamp: 5     Value: 4

        >>> right
        TimeStamp: 1     Value: 1
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4
        """
        if hasattr(left_interp_func, '__call__'):
            interpolator_left = utils.Interpolator(self._tsc, left_interp_func)
        else:
            interpolator_left = left_interp_func

        if hasattr(right_interp_func, '__call__'):
            interpolator_right = utils.Interpolator(self._tsc, right_interp_func)
        else:
            interpolator_right = right_interp_func

        pair = self._j_ts.fullAlign(
            time_series._j_ts,
            interpolator_left,
            interpolator_right
        )

        return (
            self._res_ts(TimeSeries(self._tsc, pair.left())),
            self._res_ts(TimeSeries(self._tsc, pair.right()))
        )

    def full_join(self, time_series, join_func=None, left_interp_func=lambda h, f, ts: None,
                  right_interp_func=lambda h, f, ts: None):
        """join two time-series based on a temporal full join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

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
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal full join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.full_join(orig_right, interpolator_left=interpolators.prev(), interpolator_right=interpolators.next())
        >>> ts
        TimeStamp: 1     Value: [1, 1]
        TimeStamp: 2     Value: [1, 1]
        TimeStamp: 3     Value: [3, 2]
        TimeStamp: 4     Value: [4, 3]
        TimeStamp: 5     Value: [4, 4]
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
            interpolator_right  = right_interp_func

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.fullJoin(
                time_series._j_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator_left,
                interpolator_right,
            )
        ))

    def left_align(self, time_series, interp_func=lambda h, f, ts: None):
        """align two time-series based on a temporal left join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        align the two time-series based on a temporal left join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> (left, right) = orig_left.left_align(orig_right, interpolators.prev(), interpolators.next())
        >>> left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> right
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_ts.leftAlign(
            time_series._j_ts,
            interpolator
        )

        return (
            self._res_ts(TimeSeries(self._tsc, pair.left())),
            self._res_ts(TimeSeries(self._tsc, pair.right()))
        )

    def left_join(self, time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two time-series based on a temporal left join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal left join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.left_join(orig_right, inter_func=interpolators.next())
        >>> ts
        TimeStamp: 1     Value: [1, 1]
        TimeStamp: 3     Value: [3, 2]
        TimeStamp: 4     Value: [4, 3]
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.leftJoin(
                time_series._j_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def right_align(self, time_series, interp_func=lambda h, f, ts: None):
        """align two time-series based on a temporal right join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        align the two time-series based on a temporal right join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> (left, right) = orig_left.right_align(orig_right, interpolators.prev())
        >>> left
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4
        TimeStamp: 5     Value: 4

        >>> right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_ts.rightAlign(
            time_series._j_ts,
            interpolator
        )

        return (
            self._res_ts(TimeSeries(self._tsc, pair.left())),
            self._res_ts(TimeSeries(self._tsc, pair.right()))
        )

    def right_join(self, time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two time-series based on a temporal right join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal right join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.right_join(orig_right, interp_func=interpolators.prev())
        >>> ts
        TimeStamp: 2     Value: [1, 1]
        TimeStamp: 3     Value: [3, 2]
        TimeStamp: 4     Value: [4, 3]
        TimeStamp: 5     Value: [4, 4]
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.rightJoin(
                time_series._j_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def left_outer_align(self, time_series, interp_func=lambda h, f, ts: None):
        """align two time-series based on a temporal left outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        align the two time-series based on a temporal left outer join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> (left, right) = orig_left.left_outer_align(orig_right, interpolators.next())
        >>> left
        TimeStamp: 1     Value: 1

        >>> right
        TimeStamp: 1     Value: 1
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_ts.leftOuterAlign(
            time_series._j_ts,
            interpolator
        )

        return (
            self._res_ts(TimeSeries(self._tsc, pair.left())),
            self._res_ts(TimeSeries(self._tsc, pair.right()))
        )

    def left_outer_join(self, time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two time-series based on a temporal left outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal left outer join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.left_outer_join(orig_right, interp_func=interpolators.next())
        >>> ts
        TimeStamp: 1     Value: [1, 1]
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.leftOuterJoin(
                time_series._j_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    def right_outer_align(self, time_series, interp_func=lambda h, f, ts: None):
        """align two time-series based on a temporal right outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        tuple
            aligned time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        align the two time-series based on a temporal right outer join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> (left, right) = orig_left.right_outer_align(orig_right, interpolators.prev())
        >>> left
        TimeStamp: 2     Value: 1
        TimeStamp: 5     Value: 4

        >>> right
        TimeStamp: 2     Value: 1
        TimeStamp: 5     Value: 4
        """
        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        pair = self._j_ts.rightOuterAlign(
            time_series._j_ts,
            interpolator
        )

        return (
            self._res_ts(TimeSeries(self._tsc, pair.left())),
            self._res_ts(TimeSeries(self._tsc, pair.right()))
        )

    def right_outer_join(self, time_series, join_func=None, interp_func=lambda h, f, ts: None):
        """join two time-series based on a temporal right outer join strategy and optionally interpolate missing values

        Parameters
        ----------
        time_series : :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            the time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Examples
        ----------
        create two simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> orig_left = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(1,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,3))\
            .add(autoai_ts_libs.deps.tspy.observation(4,4))\
            .result()\
            .to_time_series()
        >>> orig_right = autoai_ts_libs.deps.tspy.builder()\
            .add(autoai_ts_libs.deps.tspy.observation(2,1))\
            .add(autoai_ts_libs.deps.tspy.observation(3,2))\
            .add(autoai_ts_libs.deps.tspy.observation(4,3))\
            .add(autoai_ts_libs.deps.tspy.observation(5,4))\
            .result()\
            .to_time_series()
        >>> orig_left
        TimeStamp: 1     Value: 1
        TimeStamp: 3     Value: 3
        TimeStamp: 4     Value: 4

        >>> orig_right
        TimeStamp: 2     Value: 1
        TimeStamp: 3     Value: 2
        TimeStamp: 4     Value: 3
        TimeStamp: 5     Value: 4

        join the two time-series based on a temporal right outer join strategy

        >>> from autoai_ts_libs.deps.tspy.functions import interpolators
        >>> ts = orig_left.right_outer_join(orig_right, interp_func=interpolators.prev())
        >>> ts
        TimeStamp: 2     Value: [1, 1]
        TimeStamp: 5     Value: [4, 4]
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return self._res_ts(TimeSeries(
            self._tsc,
            self._j_ts.rightOuterJoin(
                time_series._j_ts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        ))

    # actions go here
    # actions are any operations that cause the time series to get its values

    def forecast(self, num_predictions, fm, start_training_time=None, confidence=None):
        """forecast the next num_predictions using a forecasting model

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
        :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
            a collection of observations

        Raises
        --------
        TSErrorWithMessage
            If there is an error with TimeSeries handling

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts = autoai_ts_libs.deps.tspy.time_series([float(i) for i in range(10)])
        >>> ts
        TimeStamp: 0     Value: 0.0
        TimeStamp: 1     Value: 1.0
        TimeStamp: 2     Value: 2.0
        TimeStamp: 3     Value: 3.0
        TimeStamp: 4     Value: 4.0
        TimeStamp: 5     Value: 5.0
        TimeStamp: 6     Value: 6.0
        TimeStamp: 7     Value: 7.0
        TimeStamp: 8     Value: 8.0
        TimeStamp: 9     Value: 9.0

        forecast the next 5 values using an auto forecastor

        >>> num_predictions = 5
        >>> model = autoai_ts_libs.deps.tspy.forecasters.auto(8)
        >>> confidence = .99
        >>> predictions = ts.forecast(num_predictions, model, confidence=confidence)
        >>> predictions.to_time_series()
        TimeStamp: 10     Value: Prediction(value=10.0, lower_bound=10.0, upper_bound=10.0, error=0.0)
        TimeStamp: 11     Value: Prediction(value=10.997862810553725, lower_bound=9.934621260488143, upper_bound=12.061104360619307, error=0.41277640121597475)
        TimeStamp: 12     Value: Prediction(value=11.996821082897318, lower_bound=10.704895525154571, upper_bound=13.288746640640065, error=0.5015571318964149)
        TimeStamp: 13     Value: Prediction(value=12.995779355240911, lower_bound=11.50957896664928, upper_bound=14.481979743832543, error=0.5769793776877866)
        TimeStamp: 14     Value: Prediction(value=13.994737627584504, lower_bound=12.33653268707341, upper_bound=15.652942568095598, error=0.6437557559526337)
        """
        from autoai_ts_libs.deps.tspy.data_structures.forecasting import ForecastingModel
        if isinstance(fm, ForecastingModel.ForecastingModel):
            j_fm = self._tsc._jvm.com.ibm.research.time_series.transforms.forecastors.Forecasters.general(fm._j_fm)
        else:
            j_fm = fm

        try:
            if start_training_time is None:
                j_observations = self._j_ts.forecast(num_predictions, j_fm, 1.0 if confidence is None else confidence)
            else:
                if isinstance(start_training_time, datetime.datetime):
                    if start_training_time.tzinfo is None or start_training_time.tzinfo.utcoffset(
                            start_training_time) is None:  # this is a naive datetime, must make it aware
                        start_training_time = start_training_time.replace(tzinfo=datetime.timezone.utc)

                    j_start = self._tsc._jvm.java.time.ZonedDateTime.parse(
                        str(start_training_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
                        self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
                    )
                else:
                    j_start = start_training_time

                j_observations = self._j_ts.forecast(num_predictions, j_fm, j_start,  1.0 if confidence is None else confidence)
            ts_builder = self._tsc.observations.builder()
            from autoai_ts_libs.deps.tspy.data_structures import Prediction
            if confidence is None:
                for j_obs in j_observations.iterator():
                    ts_builder.add((
                        j_obs.getTimeTick(),
                        Prediction(self._tsc, j_obs.getValue()).value
                    ))
            else:
                for j_obs in j_observations.iterator():
                    ts_builder.add((
                        j_obs.getTimeTick(),
                        Prediction(self._tsc, j_obs.getValue())
                    ))
            return ts_builder.result()

        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            msg = "There was an issue forecasting, this may be caused by incorrect types given to chained operations"
            raise TSErrorWithMessage(msg)

    def cache(self, cache_size=None):
        """suggest to the time-series to cache values

        Parameters
        ----------
        cache_size : int, optional
            the max cache size (default is max long)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series

        Notes
        -----
        this is a lazy operation and will only suggest to the time-series to save values once computed
        """
        if cache_size is None:
            return TimeSeries(self._tsc, self._j_ts.cache())
        else:
            return TimeSeries(self._tsc, self._j_ts.cache(cache_size))

    def uncache(self):
        """remove the time-series caching mechanism

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries.TimeSeries`
            a new time-series
        """
        return TimeSeries(self._tsc, self._j_ts.uncache())

    def count(self, inclusive=False):
        """count the current number of observations in this time-series

        Parameters
        ----------
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        int
            the number of observations in this time-series
        """
        return self._j_ts.count(inclusive)

    def describe(self):
        """retrieve time-series statistics computed from all values in this time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.Stats.Stats` or :class:`~autoai_ts_libs.deps.tspy.data_structures.NumStats.NumStats`
            the basic statistics for this time-series or additional numeric statistics if float
        """
        collected = self.materialize()
        type_determined = ""
        if not collected.is_empty():
            type_determined = type(collected.first().value)

        if type_determined is float or type_determined is int:
            from autoai_ts_libs.deps.tspy.data_structures.NumStats import NumStats
            stats = NumStats(
                self._tsc,
                self._j_ts.reduce(
                    self._tsc._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.describeNumeric()
                )
            )
        else:
            from autoai_ts_libs.deps.tspy.data_structures.Stats import Stats
            stats = Stats(self._tsc, self._j_ts.describe())

        return stats

    def reduce(self, *args):
        """reduce this time-series or two time-series to a single value

        Parameters
        ----------
        args : list of arguments
            if one arg given, a unary reducer is used. If two args given, a time-series and binary reducer are used.

        Returns
        -------
        any
            the output of time-series reduction

        Raises
        --------
        ValueError
            If there is an error in the input arguments, e.g. not a supporting data type
        TSErrorWithMessage
            If there is an error with TimeSeries handling

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        reduce this time-series to an average

        >>> from autoai_ts_libs.deps.tspy.functions import reducers
        >>> avg = ts_orig.reduce(reducers.average())
        >>> avg
        3

        reduce this time-series and another to a cross-correlation

        >>> from autoai_ts_libs.deps.tspy.functions import reducers
        >>> other_ts = autoai_ts_libs.deps.tspy.time_series([2.0, 3.0, 4.0])
        >>> cross_correlation = ts_orig.reduce(other_ts, reducers.cross_correlation())
        >>> cross_correlation
        [-0.49999999999999994, 4.4408920985006264e-17, 1.0, 4.4408920985006264e-17, -0.49999999999999994]
        """
        try:
            if len(args) == 0:
                raise ValueError("must provide at least one argument")
            elif len(args) == 1:
                return self._j_ts.reduce(args[0])
            else:
                return self._j_ts.reduce(args[0]._j_ts, args[1])
        except Py4JJavaError as e:
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            raise TSErrorWithMessage("There was an issue reducing, this may be caused by incorrect types given to "
                              "chained operations")

    def collect(self, inclusive=False):
        return self.materialize(inclusive=inclusive)

    def get_values(self, start, end, inclusive=False):
        return self.materialize(start, end, inclusive)

    def materialize(self, start=None, end=None, inclusive=False):
        """get all values between a range in this time-series

        Parameters
        ----------
        start : int or datetime, optional
            start of range, inclusive (default is first observation of time-series)
        end : int or datetime, optional
            end of range, inclusive (default is last observation of time-series)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
            a collection of observations

        Raises
        --------
        TSErrorWithMessage
            If there is an error with TimeSeries handling

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        get values in range start=1, end=3

        >>> observations = ts.materialize(1, 3)
        >>> observations
        [(1,2.0),(2,3.0)]

        get values in a range using slice

        >>> observations = ts[1:-1]
        >>> observations
        [(1,2.0)]

        collect all the values

        >>> ts_org.materialize()
        [(0,1.0),(1,2.0),(2,3.0)]
        """
        if start is None and end is None:
            try:
                return BoundTimeSeries.BoundTimeSeries(self._tsc, self._j_ts.materialize(inclusive))
            except Py4JJavaError as e:
                if self._tsc._kill_gateway_on_exception:
                    self._tsc._gateway.shutdown()
                raise TSErrorWithMessage(
                    "There was an issue collecting data, this may be caused by incorrect types given to "
                    "chained operations")
        else:
            if start is None or end is None:
                bounds = self._j_ts.estimateRange()
                if start is None:
                    start = bounds.left()
                else:
                    end = bounds.right()

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
                    return BoundTimeSeries.BoundTimeSeries(self._tsc, self._j_ts.materialize(j_zdt_start, j_zdt_end, inclusive))
                else:
                    return BoundTimeSeries.BoundTimeSeries(self._tsc, self._j_ts.materialize(start, end, inclusive))
            except(Py4JJavaError):
                if self._tsc._kill_gateway_on_exception:
                    self._tsc._gateway.shutdown()
                raise TSErrorWithMessage("There was an issue collecting data, this may be caused by incorrect types given to "
                                  "chained operations")

    def print(self, start=None, end=None, inclusive=False, human_readable=True):
        """print this time-series

        Parameters
        ----------
        start : int or datetime, optional
            start of range (inclusive) (default is current first time-tick)
        end : int or datetime
            end of range (inclusive) (default is current last time-tick)
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)
        human_readable : bool, optional
            if true, will print time-stamps as human readable if time-series is backed by time-reference-system,
            otherwise will print time-ticks

        Raises
        --------
        ValueError
            If there is an error in the input arguments, e.g. not a supporting data type
        """
        if start is None and end is None:
            observations = self.materialize(inclusive=inclusive)
        elif start is not None and end is not None:
            observations = self.materialize(start, end, inclusive)
        else:
            # todo we can fix this
            raise ValueError("start and end must both either be set or be None")
        for obs in observations:
            if human_readable:
                print(obs._to_human_readable_str(self._j_ts.getTRS()))
            else:
                print(obs)

    def find(self, func_or_value, find_first=True):
        from py4j.java_gateway import JavaObject
        if hasattr(func_or_value, '__call__'):
            func_or_value = utils.FilterFunction(self._tsc, func_or_value)
        elif isinstance(func_or_value, JavaObject):
            func_or_value = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func_or_value)
        else:
            from autoai_ts_libs.deps.tspy.functions import expressions as e
            func_or_value = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(
                e.eq(e.id(), func_or_value)
            )
        j_opt_obs = self._j_ts.find(func_or_value, find_first)
        if not j_opt_obs.isPresent():
            return None
        else:
            from autoai_ts_libs.deps.tspy.data_structures import Observation
            j_obs = j_opt_obs.get()
            return Observation(self._tsc, j_obs.getTimeTick(), j_obs.getValue())



    def to_df(self, inclusive=False):
        """convert this time-series to a pandas dataframe

        Parameters
        ----------
        inclusive : bool, optional
            if true, will use inclusive bounds (default is False)

        Returns
        -------
        dataframe
            a pandas dataframe representation of this time-series

        Examples
        ----------
        create a simple time-series

        >>> import autoai_ts_libs.deps.tspy
        >>> ts_orig = autoai_ts_libs.deps.tspy.time_series([1.0, 2.0, 3.0])
        >>> ts_orig
        TimeStamp: 0     Value: 1
        TimeStamp: 1     Value: 2
        TimeStamp: 2     Value: 3

        convert time-series to pandas dataframe

        >>> df = ts_orig.to_df()
        >>> df
           timestamp  value
        0          0      1
        1          1      2
        2          2      3
        """
        from io import StringIO
        csv_str = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.saveTimeSeriesAsJsonString(self._j_ts, inclusive)
        import pandas as pd
        return pd.read_json(StringIO(csv_str), orient="records")

    def __str__(self):
        """

        Raises
        --------
        TSErrorWithMessage
            If there is an error with TimeSeries handling
        """
        try:
            return self._j_ts.toString()
        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            raise TSErrorWithMessage("There was an issue collecting data, this may be caused by incorrect types given to "
                              "chained operations")

    def __repr__(self):
        """
        Raises
        --------
        TSErrorWithMessage
            If there is an error with TimeSeries handling

        """
        try:
            return self._j_ts.toString()
        except(Py4JJavaError):
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            raise TSErrorWithMessage("There was an issue collecting data, this may be caused by incorrect types given to "
                              "chained operations")

    def __len__(self):
        return self.count()

    def __getitem__(self, item):
        """

        Raises
        --------
        TSErrorWithMessage
            If there is an error with TimeSeries handling
        """
        if isinstance(item, slice):
            bounds = self._j_ts.estimateRange()
            min = bounds.left()
            max = bounds.right()
            current = self
            if item.step is not None:
                current = current.resample(item.step, self._tsc.interpolators.fill(None))

            if item.start is None and item.stop is None:
                start = min
                stop = max
            elif item.stop is None:
                start = max + item.start + 1 if item.start < 0 else item.start
                stop = max
            elif item.start is None:
                start = min
                stop = max + item.stop if item.stop < 0 else item.stop
            else:
                start = max + item.start + 1 if item.start < 0 else item.start
                stop = max + item.stop if item.stop < 0 else item.stop

            return current.materialize(start, stop)
        elif isinstance(item, tuple):
            if isinstance(item[0], datetime.datetime) and isinstance(item[1], datetime.datetime):
                return self.materialize(item[0], item[1])
            else:
                raise TSErrorWithMessage("If slicing with tuple, you must use datetime")
        else:
            raise TSErrorWithMessage("TimeSeries range indexing requires either a (datetime, datetime) or a slice")

