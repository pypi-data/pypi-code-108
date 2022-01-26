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

import datetime as datetime

from py4j.java_collections import ListConverter

from autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.MultiObservationStream import MultiObservationStream
from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries import MultiTimeSeries
from autoai_ts_libs.deps.tspy.data_structures import utils


class StreamMultiTimeSeries:
    """
    This is the data-structure to handle multiple time-series in motion where each time-series is denoted by a unique
    key. Stream-Multi-Time-Series can be thought of as a FIFO queue, having a peek and poll method. A unique quality of
    Stream-Multi-Time-Series is that it allows for a rich set of segmentation functions which are blocking by nature
    (will not resolve till a full window is uncovered). Because of this, Stream-Multi-Time-Series has an extremely low
    memory footprint when executing on large amounts of data as well.

    Examples
    --------
    create a simple queue

    >>> import queue
    >>> key_observation_queue = queue.Queue()

    create a simple stream-multi-time-series from a queue

    >>> import autoai_ts_libs.deps.tspy
    >>> smts = autoai_ts_libs.deps.tspy.stream_multi_time_series.queue(key_observation_queue)

    create a background thread adding to the queue

    >>> from threading import Thread
    >>> from time import sleep
    >>> def thread_function():
        ...c = 0
        ...while True:
        ...     observation = autoai_ts_libs.deps.tspy.observation(c, c)
        ...     key = "a" if c % 2 == 0 else "b"
        ...     c = c + 1
        ...     key_observation_queue.put_nowait((key, observation))
        ...     sleep(1)
    >>> thread = Thread(target = thread_function)
    >>> thread.start()

    continuously get values from the queue

    >>> for mts in smts:
    ...     print(mts)
    """

    def __init__(self, tsc, j_stream_mts, trs=None):
        self._tsc = tsc
        self._j_stream_mts = j_stream_mts
        self._trs = trs

    def __next__(self):
        return MultiTimeSeries(self._tsc, self._j_stream_mts.poll())

    def __iter__(self):
        while True:
            yield self.__next__()

    def run(self):
        """
        run the streaming pipeline

        Notes
        -----
        if the stream is backed by an infinite source, this will never end until the program is explicitly killed
        """
        self._j_stream_mts.run()

    def add_sink(self, multi_data_sink):
        """
        add a multi-data-sink to this piece of the streaming pipeline.

        Parameters
        ----------
        multi_data_sink : :class:`~autoai_ts_libs.deps.tspy.io.MultiDataSink.MultiDataSink`
            the multi-data-sink to output this piece of the pipeline to

        Returns
        -------
        :class`autoai_ts_libs.deps.tspy.data_structures.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Examples
        --------
        create a stream-multi-time-series from a queue

        >>> import queue
        >>> import autoai_ts_libs.deps.tspy
        >>> q = queue.Queue()
        >>> mts = autoai_ts_libs.deps.tspy.stream_multi_time_series.queue(q)

        create a datasink

        >>> from autoai_ts_libs.deps.tspy.io.MultiDataSink import MultiDataSink
        >>> class MySink(MultiDataSink):
            ...def dump(self, observations_dict):
            ...     print(observations_dict)

        add the datasink to the time-series

        >>> mts_with_sink = mts.add_sink(MySink())
        """
        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.addSink(utils.JavaMultiDataSink(self._tsc, multi_data_sink))
        )

    def partition(self, num_partitions=-1, partition_polling_interval=1000):
        """
        partition this stream-multi-time-series such that all partitions can be run on separate threads in parallel

        Parameters
        ----------
        num_partitions : int
            number of partitions
        partition_polling_interval : int, optional
            how often to poll for new values on each partition (default is 1000 ms)

        Returns
        -------
        :class`autoai_ts_libs.deps.tspy.data_structures.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new partitioned stream-multi-time-series
        """
        if num_partitions == -1:
            num_partitions = self._tsc._jvm.java.lang.Runtime.getRuntime().availableProcessors()
        return StreamMultiTimeSeries(
            self._tsc, self._j_stream_mts.partition(num_partitions, partition_polling_interval))

    def to_multi_observation_stream(self):
        """
        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.MultiObservationStream.MultiObservationStream`
            a stream iterator of (key, observation)
        """
        return MultiObservationStream(self._tsc, self._j_stream_mts.toMultiObservationStream())

    def peek(self):
        """
        Optionally get the most recent values in the queue without flushing the queue.

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a multi-time-series containing the most recent resolved observations. If no observations exist,
            return None
        """
        opt_j_mts = self._j_stream_mts.peek()
        if opt_j_mts.isPresent():
            return MultiTimeSeries(self._tsc, opt_j_mts.get())
        else:
            return None

    def poll(self, polling_interval=-1):
        """
        Get the most recent values in the queue. If no values exists, this method will block and poll at the rate of the
        given polling_interval. Once values have been resolved, poll will flush the queue up till the last values
        time-tick

        Parameters
        ----------
        polling_interval : int, optional
            how often to poll for values if none exist in the queue (default is 0ms)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
            a multi-time-series containing the most recent resolved observations.
        """
        return MultiTimeSeries(self._tsc, self._j_stream_mts.poll(polling_interval))

    def with_trs(self, granularity=datetime.timedelta(milliseconds=1), start_time=datetime.datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)):
        """create a new stream-multi-time-series with its timestamps mapped based on a granularity and start_time. In
        the scope of this method, granularity refers to the granularity at which to see time_ticks and start_time refers
        to the zone-date-time in which to start your stream-multi-time-series

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in stream-multi-time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is 1ms)
        start_time : datetime, optional
            the starting date-time of the stream-multi-time-series (default is 1970-01-01 UTC)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series with its time_ticks mapped based on a new :class:`~autoai_ts_libs.deps.tspy.utils.TRS.TRS`.

        Notes
        -----
        time_ticks will be mapped as follows - (current_time_tick - start_time) / granularity

        if the source stream-multi-time-series does not have a time-reference-system associated with it, this method will
        throw and exception
        """
        j_time_tick = self._tsc._jvm.java.time.Duration.ofMillis(
            int(((granularity.microseconds + (
                        granularity.seconds + granularity.days * 24 * 3600) * 10 ** 6) / 10 ** 6) * 1000)
        )

        if start_time.tzinfo is None or start_time.tzinfo.utcoffset(
                start_time) is None:  # this is a naive datetime, must make it aware
            import datetime
            start_time = start_time.replace(tzinfo=datetime.timezone.utc)

        j_zdt = self._tsc._jvm.java.time.ZonedDateTime.parse(
            str(start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")),
            self._tsc._jvm.java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS[XXX][X]")
        )

        j_trs = self._tsc._jvm.com.ibm.research.time_series.core.utils.TRS.of(j_time_tick, j_zdt)

        from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
        trs = TRS(self._tsc, granularity, start_time, j_trs)
        return StreamMultiTimeSeries(self._tsc, self._j_stream_mts.withTRS(j_trs), trs)

    def interval_join(self, right_stream_mts, filter_func, left_delta, right_delta):
        """join two stream-multi-time-series where observations in the right stream lie within an interval of this
        stream. The interval is defined by a point (discovered from the filter_func) with left_delta time-ticks to the
        left and right_delta time-ticks to the right.

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-time-series to align with
        filter_func : func
            function which given a value, will return whether to form an interval
        left_delta : int
            how many time-ticks to the left of the interval-point
        right_delta : int
            how many time-ticks to the right of the interval-point

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series
        """
        if hasattr(filter_func, '__call__'):
            filter_func = utils.FilterFunction(self._tsc, filter_func)
        else:
            filter_func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(
                filter_func)
        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.intervalJoin(right_stream_mts._j_stream_mts, filter_func, left_delta, right_delta),
            self._trs
        )

    def resample(self, periodicity, interpolator):
        """produce a new stream-muliti-time-series by resampling the current stream-multi-time-series to a given
        periodicity

        Parameters
        ----------
        period : int
            the period to resample to
        func : func or interpolator
            the interpolator method to be used when a value doesn't exist at a given time-tick

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.resample` for usage
        """
        if hasattr(interpolator, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interpolator)

        return StreamMultiTimeSeries(self._tsc, self._j_stream_mts.resample(periodicity, interpolator), self._trs)

    def fillna(self, interpolator, null_value=None):
        """produce a new stream-multi-time-series which is the result of filling all null values.

        Parameters
        ----------
        interpolator : func or interpolator
            the interpolator method to be used when a value is null
        null_value : any, optional
            denotes a null value, for instance if nullValue = NaN, NaN would be filled

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.fillna` for usage
        """
        if hasattr(interpolator, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interpolator)

        return StreamMultiTimeSeries(self._tsc, self._j_stream_mts.fillna(interpolator, null_value), self._trs)

    def inner_join(self, right_stream_mts, join_func=None):
        """join two stream-multi-time-series based on a temporal inner join strategy

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-time-series to join with

        join_func : func, optional
            function to join 2 values at a given time-tick. If None given, joined value will be in a list
            (default is None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.inner_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client) #this can be done through a canned lambda for performance purposes

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.innerJoin(
                right_stream_mts._j_stream_mts,
                utils.BinaryMapFunction(self._tsc, join_func)
            )
        )

    def left_join(self, right_stream_mts, join_func=None, interp_func=lambda h, f, ts: None):
        """join two stream-multi-time-series based on a temporal left join strategy and optionally interpolate missing
        values

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-multi-time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right stream-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.left_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.leftJoin(
                right_stream_mts._j_stream_mts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        )

    def right_join(self, right_stream_mts, join_func=None, interp_func=lambda h, f, ts: None):
        """join two stream-multi-time-series based on a temporal right join strategy and optionally interpolate missing
        values

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-multi-time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left stream-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.right_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.rightJoin(
                right_stream_mts._j_stream_mts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        )

    def left_outer_join(self, right_stream_mts, join_func=None, interp_func=lambda h, f, ts: None):
        """join two stream-multi-time-series based on a temporal left outer join strategy and optionally interpolate
        missing values

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-multi-time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the right stream-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.left_outer_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.leftOuterJoin(
                right_stream_mts._j_stream_mts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        )

    def right_outer_join(self, right_stream_mts, join_func=None, interp_func=lambda h, f, ts: None):
        """join two stream-multi-time-series based on a temporal right outer join strategy and optionally interpolate
        missing values

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-multi-time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        interp_func : func or interpolator, optional
            the left stream-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.right_outer_join` for usage
        """
        if join_func is None:
            join_func = lambda l, r: ListConverter().convert([l, r], self._tsc._gateway._gateway_client)

        if hasattr(interp_func, '__call__'):
            interpolator = utils.Interpolator(self._tsc, interp_func)
        else:
            interpolator = interp_func

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.rightOuterJoin(
                right_stream_mts._j_stream_mts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator
            )
        )

    def full_join(self, right_stream_mts, join_func=None, left_interp_func=lambda h, f, ts: None,
                  right_interp_func=lambda h, f, ts: None):
        """join two stream-multi-time-series based on a temporal full join strategy and optionally interpolate missing
        values

        Parameters
        ----------
        right_stream_mts : :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            the stream-multi-time-series to align with

        join_func : func, optional
            function to join to values (default is join to list where left is index 0, right is index 1)

        left_interp_func : func or interpolator, optional
            the left stream-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        right_interp_func : func or interpolator, optional
            the right stream-time-series interpolator method to be used when a value doesn't exist at a given time-tick
            (default is fill with None)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.full_join` for usage
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

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.fullJoin(
                right_stream_mts._j_stream_mts,
                utils.BinaryMapFunction(self._tsc, join_func),
                interpolator_left,
                interpolator_right
            )
        )

    def map(self, func):
        """produce a new stream-multi-time-series where each observation's value in this stream-time-series is mapped to
        a new observation value

        Parameters
        ----------
        func : func
            value mapping function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series with its values re-mapped

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.map` for usage
        """
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        from autoai_ts_libs.deps.tspy.functions import expressions
        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.map(expressions._wrap_object_expression(func)),
            self._trs
        )

    def map_with_key(self, func):
        """produce a new stream-multi-time-series where each observation's value in this stream-time-series is mapped
        given a key and value function to a new observation value

        Parameters
        ----------
        func : func
            value mapping function which given a key and value, returns a value

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series with its values re-mapped
        """
        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.mapWithKey(utils.BinaryMapFunction(self._tsc, func)),
            self._trs
        )

    def flatmap(self, func):
        """produce a new stream-multi-time-series where each observation's value in this stream-multi-time-series is
        mapped to 0 to N new values.

        Parameters
        ----------
        func : func
            value mapping function which returns a list of values

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series with its values flat-mapped

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.flatmap` for usage

        an observations time-tick will be duplicated if a single value maps to multiple values
        """
        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.flatMap(utils.FlatUnaryMapFunction(self._tsc, func)),
            self._trs
        )

    def filter(self, func):
        """produce a new stream-multi-time-series which is the result of filtering by each observation's value given a
        filter function.

        Parameters
        ----------
        func : func
            the filter on observation's value function

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.filter` for usage
        """
        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.filter(func),
            self._trs
        )

    def segment(self, window, step=1):
        """produce a new segment-multi-time-series from a performing a sliding-based segmentation over each time-series.

        Parameters
        ----------
        window : int
            number of observations per window
        step : int, optional
            step size to slide (default is 1)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.SegmentStreamMultiTimeSeries.SegmentStreamMultiTimeSeries`
            a new segment-stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.segment` for usage

        Segment size is guaranteed to be equal to given window value
        """
        from autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.SegmentStreamMultiTimeSeries import SegmentStreamMultiTimeSeries
        return SegmentStreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.segment(window, step),
            self._trs
        )

    def segment_by_time(self, window, step=None):
        """produce a new segment-time-series from a performing a time-based segmentation over each time-series

        Parameters
        ----------
        window : int
            time-tick length of window
        step : int
            time-tick length of step

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.SegmentStreamMultiTimeSeries.SegmentStreamMultiTimeSeries`
            a new segment-stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.segment_by_time` for usage
        """
        if step is None:
            step = window
        from autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.SegmentStreamMultiTimeSeries import SegmentStreamMultiTimeSeries
        return SegmentStreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.segmentSeriesByTime(window, step),
            self._trs
        )

    def segment_by_anchor(self, func, left_delta, right_delta):
        """produce a new segment-time-series from performing an anchor-based segmentation over each time-series. An
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

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.SegmentStreamTimeSeries.SegmentStreamMultiTimeSeries`
            a new segment-stream-multi-time-series

        Notes
        -----
        see :func:`~autoai_ts_libs.deps.tspy.data_structures.TimeSeries.TimeSeries.segment_by_anchor` for usage
        """
        if hasattr(func, '__call__'):
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)
        from autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.SegmentStreamMultiTimeSeries import SegmentStreamMultiTimeSeries
        return SegmentStreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.segmentSeriesByAnchor(func, left_delta, right_delta),
            self._trs
        )

