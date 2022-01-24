
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
from py4j.protocol import Py4JJavaError

from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures import utils
from autoai_ts_libs.deps.tspy.data_structures.transforms import UnaryTransform, BinaryTransform
from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage


class BoundTimeSeries:
    """
    A special form of materialized time-series (sorted collection) whose values are of type
    :class:`.Observation`.

    An observation-collection has the following properties:

    1. Sorted by observation time-tick
    2. Support for observations with duplicate time-ticks
    3. Duplicate time-ticks will keep ordering

    Examples
    --------
    create an observation-collection

    >>> import autoai_ts_libs.deps.tspy
    >>> ts_builder = autoai_ts_libs.deps.tspy.builder()
    >>> ts_builder.add(autoai_ts_libs.deps.tspy.observation(1,1))
    >>> ts_builder.add(autoai_ts_libs.deps.tspy.observation(2,2))
    >>> ts_builder.add(autoai_ts_libs.deps.tspy.observation(1,3))
    >>> observations = ts_builder.result()
    >>> observations
    [(1,1),(1,3),(2,2)]

    iterate through this collection

    >>> for o in observations:
        ...print(o.time_tick, ",", o.value)
    1 , 1
    1 , 3
    2 , 2
    """

    def __init__(self, tsc, j_observations=None):
        self._tsc = tsc
        self._obj_type = None
        self._j_observations = j_observations

    @property
    def trs(self):
        """
        Returns
        -------
        TRS : :class:`~autoai_ts_libs.deps.tspy.utils.TRS.TRS`
            this time-series time-reference-system
        """
        return self._j_observations.getTRS()

    def contains(self, time_tick):
        """
        Checks for containment of time-tick within the collection

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        bool
            True if an observation in this collection has the given time-tick, otherwise False
        """
        return self._j_observations.contains(time_tick)

    def ceiling(self, time_tick):
        """
        get the ceiling observation for the given time-tick. The ceiling is defined as the the observation which bares
        the same time-tick as the given time-tick, or if one does not exist, the next higher observation. If no such
        observation exists that satisfies these arguments, in the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the ceiling observation
        """
        return self.__obs_as_py(self._j_observations.ceiling(time_tick))

    def floor(self, time_tick):
        """
        get the floor observation for the given time-tick. The floor is defined as the the observation which bares
        the same time-tick as the given time-tick, or if one does not exist, the next lower observation. If no such
        observation exists that satisfies these arguments, in the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the floor observation
        """
        return self.__obs_as_py(self._j_observations.floor(time_tick))

    def higher(self, time_tick):
        """
        get the higher observation for the given time-tick. The higher is defined as the the observation which bares
        a time-tick greater than the given time-tick. If no such observation exists that satisfies these arguments, in
        the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the floor observation
        """
        return self.__obs_as_py(self._j_observations.higher(time_tick))

    def lower(self, time_tick):
        """
        get the lower observation for the given time-tick. The lower is defined as the the observation which bares
        a time-tick less than the given time-tick. If no such observation exists that satisfies these arguments, in
        the collection, None will be returned.

        Parameters
        ----------
        time_tick : int
            the time-tick

        Returns
        -------
        :class:`.Observation`
            the floor observation
        """
        return self.__obs_as_py(self._j_observations.lower(time_tick))

    def first(self):
        """
        get the first observation in this collection. The first observation is that observation which has the lowest
        timestamp in the collection. If 2 observations have the same timestamp, the first observation that was in the
        collection will be the one returned.

        Returns
        -------
        :class:`.Observation`
            the first observation in this collection
        """
        return self.__obs_as_py(self._j_observations.first())

    def last(self):
        """
        get the last observation in this collection. The last observation is that observation which has the highest
        timestamp in the collection. If 2 observations have the same timestamp, the last observation that was in the
        collection will be the one returned.

        Returns
        -------
        :class:`.Observation`
            the last observation in this collection
        """
        return self.__obs_as_py(self._j_observations.last())

    def is_empty(self):
        """checks if there is any observation

        Returns
        -------
        bool
            True if no observations exist in this collection, otherwise False
        """
        return self._j_observations.isEmpty()

    def __obs_as_py(self, j_observation):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        py_obj, obj_type = utils.cast_to_py_if_necessary(self._tsc, j_observation.getValue(), self._obj_type)
        self._obj_type = obj_type
        return Observation(self._tsc, j_observation.getTimeTick(), py_obj)

    def to_time_series(self, granularity=None, start_time=None):
        """
        convert this collection to a time-series

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
        start_time : datetime, optional
            the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

        Returns
        -------
        :class:`.TimeSeries`
            a new time-series
        """
        from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
        if granularity is None and start_time is None:
            return TimeSeries(self._tsc, self._j_observations.toTimeSeries())
        else:
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            # from autoai_ts_libs.deps.tspy.data_structures.TimeSeriesFactory import Factory
            from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
            trs = TRS(self._tsc, granularity, start_time)
            return TimeSeries(self._tsc, self._j_observations.toTimeSeries(trs._j_trs), trs)

    @property
    def size(self):
        """
        Returns
        -------
        int
            the number of observations in this collection
        """
        return self._j_observations.size()

    def __iter__(self):
        from autoai_ts_libs.deps.tspy.data_structures import utils
        j_iterator = self._j_observations.iterator()
        while j_iterator.hasNext():
            j_obs = j_iterator.next()
            py_obj, obj_type = utils.cast_to_py_if_necessary(self._tsc, j_obs.getValue(), self._obj_type)
            self._obj_type = obj_type
            yield Observation(self._tsc, j_obs.getTimeTick(), py_obj)

    def __str__(self):
        if self._j_observations is None:
            return ""
        else:
            return self._j_observations.toString()

    def __repr__(self):
        if self._j_observations is None:
            return ""
        else:
            return self._j_observations.toString()

    def __eq__(self, other):
        return self._j_observations.equals(other._j_observations)

    def __len__(self):
        return self.size

    class Java:
        """
        mapping to a compatible class in Java via Py4J
        """
        implements = ['com.ibm.research.time_series.core.utils.ObservationCollection']

    def add_annotation(self, key, annotation_reducer):
        if hasattr(annotation_reducer, '__call__'):
            annotation_reducer = utils.UnaryMapFunction(self._tsc, annotation_reducer)
        return BoundTimeSeries(self._tsc, self._j_observations.addAnnotation(key, annotation_reducer))

    def map_with_annotation(self, func):
        return BoundTimeSeries(self._tsc, self._j_observations.mapWithAnnotation(utils.BinaryMapFunction(self._tsc, func)))

    def map(self, func):
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        from autoai_ts_libs.deps.tspy.functions import expressions
        return BoundTimeSeries(self._tsc, self._j_observations.map(expressions._wrap_object_expression(func)))

    def map_with_index(self, func):
        if hasattr(func, '__call__'):
            func = utils.BinaryMapFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toBinaryMapWithIndexFunction(func)
        return BoundTimeSeries(self._tsc, self._j_observations.mapWithIndex(func))

    def flatmap(self, func):
        return BoundTimeSeries(self._tsc, self._j_observations.flatMap(utils.FlatUnaryMapFunction(self._tsc, func)))

    def filter(self, func):
        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return BoundTimeSeries(self._tsc, self._j_observations.filter(func))

    def fillna(self, interpolator, null_value=None):
        if hasattr(interpolator, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interpolator)

        return BoundTimeSeries(self._tsc, self._j_observations.fillna(interpolator, null_value))

    def transform(self, *args):
        if len(args) == 0:
            raise ValueError("must provide at least one argument")
        elif len(args) == 1:
            if issubclass(type(args[0]), UnaryTransform):
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.transform(
                      self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonUnaryTransform(
                          utils.JavaToPythonUnaryTransformFunction(self._tsc, args[0])
                      )
                    )
                )
            else:
                return BoundTimeSeries(self._tsc, self._j_observations.transform(args[0]))
        elif len(args) == 2:
            if issubclass(type(args[1]), BinaryTransform):
                return BoundTimeSeries(
                    self._tsc,
                    self._j_observations.transform(
                        args[0]._j_observations,
                        self._tsc._jvm.com.ibm.research.time_series.core.transform.python.PythonBinaryTransform(
                            utils.JavaToPythonBinaryTransformFunction(self._tsc, args[1])
                        )
                    )
                )
            else:
                return BoundTimeSeries(self._tsc, self._j_observations.transform(args[0]._j_observations, args[1]))

    def to_segments(self, segment_transform, annotation_map=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries
        if annotation_map is None:
            return BoundSegmentTimeSeries(self._tsc, self._j_observations.toSegments(segment_transform))
        else:
            return BoundSegmentTimeSeries(self._tsc, self._j_observations.toSegments(
                segment_transform, MapConverter().convert(annotation_map, self._tsc._gateway._gateway_client)))

    def segment(self, window, step=1, enforce_size=True):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries
        return BoundSegmentTimeSeries(self._tsc, self._j_observations.segment(window, step, enforce_size))

    def segment_by(self, func):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries
        return BoundSegmentTimeSeries(self._tsc, self._j_observations.segmentBy(utils.ObservationToKeyUnaryMapFunction(self._tsc, func)))

    def segment_by_time(self, window, step):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries
        return BoundSegmentTimeSeries(self._tsc, self._j_observations.segmentByTime(window, step))

    def segment_by_anchor(self, func, left_delta, right_delta, perc=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries

        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        if perc is None:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByAnchor(func, left_delta, right_delta)
            )
        else:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByAnchor(func, left_delta, right_delta, perc)
            )

    def segment_by_changepoint(self, change_point=None):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries
        if change_point is None:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByChangePoint()
            )
        else:
            return BoundSegmentTimeSeries(
                self._tsc,
                self._j_observations.segmentByChangePoint(utils.BinaryMapFunction(self._tsc, change_point))
            )

    def segment_by_marker(self, *args, **kwargs):
        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundSegmentTimeSeries import BoundSegmentTimeSeries
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

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
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

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
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

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
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

                return BoundSegmentTimeSeries(
                    self._tsc,
                    self._j_observations.segmentByMarker(
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
        return BoundTimeSeries(self._tsc, self._j_observations.lag(lag_amount))

    def shift(self, shift_amount, default_value=None):
        return BoundTimeSeries(self._tsc, self._j_observations.shift(shift_amount, default_value))

    def resample(self, period, func):
        if hasattr(func, '__call__'):
            func = utils.Interpolator(self._tsc, func)

        return BoundTimeSeries(
            self._tsc,
            self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.resample(
                self._j_observations,
                period,
                func
            )
        )

    def inner_join(self, time_series, join_func=None):
        if join_func is None:
            join_func = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.defaultJoinFunction()

        join_func = utils.BinaryMapFunction(self._tsc, join_func) if hasattr(join_func, '__call__') else join_func

        return BoundTimeSeries(self._tsc, self._j_observations.innerJoin(time_series._j_observations, join_func))

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

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.fullJoin(
                time_series._j_observations,
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

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.leftJoin(
                time_series._j_observations,
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

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.rightJoin(
                time_series._j_observations,
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

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.leftOuterJoin(
                time_series._j_observations,
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

        return BoundTimeSeries(
            self._tsc,
            self._j_observations.rightOuterJoin(
                time_series._j_observations,
                join_func,
                interpolator
            )
        )

    def forecast(self, num_predictions, fm, confidence=None):
        j_fm = self._tsc._jvm.com.ibm.research.time_series.transforms.forecastors.Forecasters.general(fm._j_fm)

        try:
            j_observations = self._j_observations.forecast(num_predictions, j_fm,
                                                           1.0 if confidence is None else confidence)
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

    def reduce(self, *args):
        try:
            if len(args) == 0:
                raise ValueError("must provide at least one argument")
            elif len(args) == 1:
                return self._j_observations.reduce(args[0])
            else:
                return self._j_observations.reduce(args[0]._j_ts, args[1])
        except Py4JJavaError as e:
            if self._tsc._kill_gateway_on_exception:
                self._tsc._gateway.shutdown()
            raise TSErrorWithMessage("There was an issue reducing, this may be caused by incorrect types given to "
                              "chained operations")

