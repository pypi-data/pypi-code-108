from py4j.java_collections import ListConverter
from py4j.protocol import Py4JJavaError

from autoai_ts_libs.deps.tspy.data_structures import BoundTimeSeries, utils
from autoai_ts_libs.deps.tspy.data_structures.transforms import UnaryTransform, BinaryTransform
from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage


class BoundMultiTimeSeries:

    def __init__(self, tsc, j_bound_mts):
        self._tsc = tsc
        self._j_bound_mts = j_bound_mts

    def __str__(self):
        return self._j_bound_mts.toString()

    def __len__(self):
        return self._j_bound_mts.size()

    def __getitem__(self, item):
        return BoundTimeSeries(self._tsc, self._j_bound_mts.get(item))

    def __iter__(self):
        for j_entry in self._j_bound_mts.entrySet():
            yield j_entry.getKey()

    def __contains__(self, item):
        return self._j_bound_mts.containsKey(item)

    def items(self):
        for j_entry in self._j_bound_mts.entrySet():
            yield j_entry.getKey(), BoundTimeSeries(self._tsc, j_entry.getValue())

    def add_annotation(self, key, annotation_reducer):
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.addAnnotation(key, annotation_reducer))

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
        >>> ts2 = autoai_ts_libs.deps.tspy.builder().add(autoai_ts_libs.deps.tspy.observation(2,4)).add(autoai_ts_libs.deps.tspy.observation(10,1)).result().to_time_series()
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

        >>> mts = mts_orig.map_series(lambda s: s.to_time_series().map(lambda x: x + 1).materialize())
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
        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.mapSeries(utils.SeriesUnaryMapFunction(self._tsc, func))
        )

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
        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.mapSeriesWithKey(utils.SeriesWithKeyUnaryMapfunctionToSeries(self._tsc, func))
        )

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
        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.mapSeriesKey(utils.UnaryMapFunction(self._tsc, func))
        )

    def map_with_annotation(self, func):
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.mapWithAnnotation(utils.BinaryMapFunction(self._tsc, func)))

    def map(self, func):
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        from autoai_ts_libs.deps.tspy.functions import expressions
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.map(expressions._wrap_object_expression(func)))

    def map_with_index(self, func):
        if hasattr(func, '__call__'):
            func = utils.BinaryMapFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toBinaryMapWithIndexFunction(func)
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.mapWithIndex(func))

    def flatmap(self, func):
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.flatMap(utils.FlatUnaryMapFunction(self._tsc, func)))

    def filter(self, func):
        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.filter(func))

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
        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.filterSeriesKey(utils.FilterFunction(self._tsc, func))
        )

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
            func = utils.BoundTimeSeriesFilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.filterSeries(func)
        )

    def fillna(self, interpolator, null_value=None):
        if hasattr(interpolator, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interpolator)

        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.fillna(interpolator, null_value))

    def transform(self, *args):
        if len(args) == 0:
            raise ValueError("must provide at least one argument")
        elif len(args) == 1:
            if issubclass(type(args[0]), UnaryTransform):
                return BoundMultiTimeSeries(
                    self._tsc,
                    self._j_bound_mts.transform(
                      self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonUnaryTransform(
                          utils.JavaToPythonUnaryTransformFunction(self._tsc, args[0])
                      )
                    )
                )
            else:
                return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.transform(args[0]))
        elif len(args) == 2:
            if issubclass(type(args[1]), BinaryTransform):
                return BoundMultiTimeSeries(
                    self._tsc,
                    self._j_bound_mts.transform(
                        args[0]._j_observations,
                        self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                            utils.JavaToPythonBinaryTransformFunction(self._tsc, args[1])
                        )
                    )
                )
            else:
                return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.transform(args[0]._j_bound_mts, args[1]))

    def to_segments(self, segment_transform):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.toSegments(segment_transform))

    def segment(self, window, step=1, enforce_size=True):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.segment(window, step, enforce_size))

    def segment_by(self, func):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.segmentBy(utils.ObservationToKeyUnaryMapFunction(self._tsc, func)))

    def segment_by_time(self, window, step):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.segmentByTime(window, step))

    def segment_by_anchor(self, func, left_delta, right_delta, perc=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries

        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        if perc is None:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.segmentByAnchor(func, left_delta, right_delta)
            )
        else:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.segmentByAnchor(func, left_delta, right_delta, perc)
            )

    def segment_by_changepoint(self, change_point=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries
        if change_point is None:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.segmentByChangePoint()
            )
        else:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.segmentByChangePoint(utils.BinaryMapFunction(self._tsc, change_point))
            )

    def segment_by_marker(self, *args, **kwargs):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentMultiTimeSeries import BoundSegmentMultiTimeSeries
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

                return BoundSegmentMultiTimeSeries(
                    self._tsc,
                    self._j_bound_mts.segmentByMarker(
                        utils.FilterFunction(self._tsc, start_marker),
                        utils.FilterFunction(self._tsc, end_marker),
                        start_inclusive,
                        end_inclusive,
                        start_on_first,
                        end_on_first
                    )
                )
            # this is a single marker
            else:
                marker = args[0]
                start_inclusive = args[1] if arg_len > 1 else True
                end_inclusive = args[2] if arg_len > 2 else True
                requires_start_and_end = args[3] if arg_len > 3 else False

                return BoundSegmentMultiTimeSeries(
                    self._tsc,
                    self._j_bound_mts.segmentByMarker(
                        utils.FilterFunction(self._tsc, marker),
                        start_inclusive,
                        end_inclusive,
                        requires_start_and_end
                    )
                )
        else:

            # this is a bi-marker (2 marker functions)
            if "start_marker" in kwargs and "end_marker" in kwargs:
                start_marker = kwargs['start_marker']
                end_marker = kwargs['end_marker']
                start_inclusive = kwargs['start_inclusive'] if 'start_inclusive' in kwargs else True
                end_inclusive = kwargs['end_inclusive'] if 'end_inclusive' in kwargs else True
                start_on_first = kwargs['start_on_first'] if 'start_on_first' in kwargs else False
                end_on_first = kwargs['end_on_first'] if 'end_on_first' in kwargs else True

                return BoundSegmentMultiTimeSeries(
                    self._tsc,
                    self._j_bound_mts.segmentByMarker(
                        utils.FilterFunction(self._tsc, start_marker),
                        utils.FilterFunction(self._tsc, end_marker),
                        start_inclusive,
                        end_inclusive,
                        start_on_first,
                        end_on_first
                    )
                )
            elif "marker" in kwargs:
                marker = kwargs['marker']
                start_inclusive = kwargs['start_inclusive'] if 'start_inclusive' in kwargs else True
                end_inclusive = kwargs['end_inclusive'] if 'end_inclusive' in kwargs else True
                requires_start_and_end = kwargs[
                    'requires_start_and_end'] if 'requires_start_and_end' in kwargs else False

                return BoundSegmentMultiTimeSeries(
                    self._tsc,
                    self._j_bound_mts.segmentByMarker(
                        utils.FilterFunction(self._tsc, marker),
                        start_inclusive,
                        end_inclusive,
                        requires_start_and_end
                    )
                )
            else:
                raise ValueError(
                    "kwargs must contain at the very least a 'start_marker' and 'end_marker' OR a 'marker' ")

    def lag(self, lag_amount):
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.lag(lag_amount))

    def shift(self, shift_amount, default_value=None):
        return BoundMultiTimeSeries(self._tsc, self._j_bound_mts.shift(shift_amount, default_value))

    def resample(self, period, func):
        if hasattr(func, '__call__'):
            func = utils.Interpolator(self._tsc, func)

        return BoundMultiTimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.resampleSeries(
                self._j_bound_mts,
                period,
                func
            )
        )

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
            return BoundMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.pairWiseTransform(
                    self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                        utils.JavaToPythonBinaryTransformFunction(self._tsc, binary_transform)
                    )
                )
            )
        else:
            return BoundMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.pairWiseTransform(binary_transform)
            )

    def inner_join(self, time_series, join_func=None):
        if join_func is None:
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func
        j_bound_mts_result = self._j_bound_mts.innerJoin(time_series._j_bound_mts, join_func)
        return BoundMultiTimeSeries(self._tsc, j_bound_mts_result)

    def full_join(self, time_series, join_func=None, left_interp_func=None, right_interp_func=None):
        if join_func is None:
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func

        if hasattr(left_interp_func, '__call__'):
            interpolator_left = utils.Interpolator(self._tsc, left_interp_func)
        else:
            if left_interp_func is None:
                interpolator_left = self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
            else:
                interpolator_left = left_interp_func

        if hasattr(right_interp_func, '__call__'):
            interpolator_right = utils.Interpolator(self._tsc, right_interp_func)
        else:
            if right_interp_func is None:
                interpolator_right = self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
            else:
                interpolator_right = right_interp_func

        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.fullJoin(
                time_series._j_bound_mts,
                join_func,
                interpolator_left,
                interpolator_right,
            )
        )

    def left_join(self, time_series, join_func=None, interp_func=None):
        if join_func is None:
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            if interp_func is None:
                interpolator = self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
            else:
                interpolator = interp_func

        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.leftJoin(
                time_series._j_bound_mts,
                join_func,
                interpolator
            )
        )

    def right_join(self, time_series, join_func=None, interp_func=None):
        if join_func is None:
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            if interp_func is None:
                interpolator = self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
            else:
                interpolator = interp_func

        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.rightJoin(
                time_series._j_bound_mts,
                join_func,
                interpolator
            )
        )

    def left_outer_join(self, time_series, join_func=None, interp_func=None):
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
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            if interp_func is None:
                interpolator = self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
            else:
                interpolator = interp_func

        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.leftOuterJoin(
                time_series._j_bound_mts,
                join_func,
                interpolator
            )
        )

    def right_outer_join(self, time_series, join_func=None, interp_func=None):
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
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            if interp_func is None:
                interpolator = self._tsc._jvm.com.ibm.research.time_series.core.core_transforms.general.GenericInterpolators.nullify()
            else:
                interpolator = interp_func

        return BoundMultiTimeSeries(
            self._tsc,
            self._j_bound_mts.rightOuterJoin(
                time_series._j_bound_mts,
                join_func,
                interpolator
            )
        )

    def reduce(self, func):
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        return {k: v for k, v in self._j_bound_mts.reduce(func).items()}
