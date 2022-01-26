"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
"""

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

def reader(stream_reader, granularity=None, start_time=None):
    """
    create a stream-multi-time-series from a stream-multi-time-series-reader

    Parameters
    ----------
    stream_time_series_reader : :class:`~autoai_ts_libs.deps.tspy.data_structures.io.PullStreamMultiTimeSeriesReader.PullStreamMultiTimeSeriesReader` or :class:`~autoai_ts_libs.deps.tspy.data_structures.io.PushStreamMultiTimeSeriesReader.PushStreamMultiTimeSeriesReader`
        a user-implemented stream-multi-time-series-reader
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
        a new stream-multi-time-series
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create

    tsc = get_or_create()
    return tsc.stream_multi_time_series.reader(stream_reader, granularity, start_time)

def text_file(path, map_func, granularity=None, start_time=None):
    """
    create a stream-multi-time-series from a text file

    Parameters
    ----------
    path : string
        path to file
    map_func : func
        function from a single line of a file to a tuple of (key, :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.Observation.Observation`) or
        None
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
        a new stream-multi-time-series
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create

    tsc = get_or_create()
    return tsc.stream_multi_time_series.text_file(path, map_func, granularity, start_time)

def queue(key_observation_queue, granularity=None, start_time=None):
    """
    create a stream-multi-time-series from a queue of observations

    Parameters
    ----------
    key_observation_queue : queue.Queue
        queue of tuples of type (key, :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.Observation.Observation`)
    granularity : datetime.timedelta, optional
        the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
    start_time : datetime, optional
        the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
        a new stream-multi-time-series

    Examples
    --------
    create a simple queue

    >>> import queue
    >>> observation_queue = queue.Queue()

    create a simple stream-multi-time-series from a queue

    >>> import autoai_ts_libs.deps.tspy
    >>> sts = autoai_ts_libs.deps.tspy.stream_multi_time_series.queue(observation_queue)
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create

    tsc = get_or_create()
    return tsc.stream_multi_time_series.queue(key_observation_queue, granularity, start_time)
