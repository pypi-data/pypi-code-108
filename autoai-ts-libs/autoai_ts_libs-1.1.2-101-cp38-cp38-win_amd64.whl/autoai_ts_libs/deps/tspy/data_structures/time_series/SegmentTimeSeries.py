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

from autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries import MultiTimeSeries
from autoai_ts_libs.deps.tspy.data_structures.time_series.TimeSeries import TimeSeries
from autoai_ts_libs.deps.tspy.data_structures import utils


class SegmentTimeSeries(TimeSeries):
    """
    A special form of time-series that consists of observations with a value of type :class:`~autoai_ts_libs.deps.tspy.data_structures.Segment.Segment`
    """

    def __init__(self, tsc, j_ts, trs=None):
        super().__init__(tsc, j_ts, trs)
        self._tsc = tsc
        self._j_segment_ts = j_ts

    # def collect(self, inclusive=False):
    #     from autoai_ts_libs.deps.tspy.data_structures.ObservationCollection import ObservationCollection
    #     from autoai_ts_libs.deps.tspy.data_structures.Observation import Observation
    #     res = ObservationCollection(self._gateway, self._jvm)
    #     for obs in ObservationCollection(self._gateway, self._jvm, self._j_segment_ts.collect(inclusive)):
    #         res.add(Observation(obs.timestamp, Segment(self._gateway, self._jvm, obs.value)))
    #     return res

    def cache(self, cache_size=None):
        if cache_size is None:
            j_seg_ts = self._j_segment_ts.cache()
        else:
            j_seg_ts = self._j_segment_ts.cache(cache_size)

        return SegmentTimeSeries(
            self._tsc,
            j_seg_ts,
            self.trs
        )

    def map(self, func):
        if hasattr(func, '__call__'):
            func = utils.UnaryMapFunction(self._tsc, func)

        return TimeSeries(
            self._tsc,
            self._j_segment_ts.map(func),
            self.trs
        )

    def flatmap(self, func):
        return TimeSeries(
            self._tsc,
            self._j_segment_ts.flatMap(utils.SegmentFlatUnaryMapFunction(self._tsc, func)),
            self.trs
        )

    # def flatten(self, key_func=None):
    #     """
    #     converts this segment-time-series into a multi-time-series where each time-series will be the result of a single
    #     segment
    #
    #     Parameters
    #     ----------
    #     key_func : func, optional
    #         operation where given a segment, produce a unique key (default is create key based on start of segment)
    #
    #     Returns
    #     -------
    #     :class:`~autoai_ts_libs.deps.tspy.data_structures.multi_time_series.MultiTimeSeries.MultiTimeSeries`
    #         a new multi-time-series
    #
    #     Notes
    #     -----
    #     this is not a lazy operation and will materialize the time-series
    #
    #     Examples
    #     --------
    #     create a simple time-series
    #
    #     >>> import autoai_ts_libs.deps.tspy
    #     >>> ts_orig = autoai_ts_libs.deps.tspy.data_structures.list([1,2,3,4,5,6])
    #     >>> ts_orig
    #     TimeStamp: 0     Value: 1
    #     TimeStamp: 1     Value: 2
    #     TimeStamp: 2     Value: 3
    #     TimeStamp: 3     Value: 4
    #     TimeStamp: 4     Value: 5
    #     TimeStamp: 5     Value: 6
    #
    #     segment the time-series using a simple sliding window
    #
    #     >>> ts_sliding = ts_orig.segment(2)
    #     >>> ts_sliding
    #     TimeStamp: 0     Value: original bounds: (0,1) actual bounds: (0,1) observations: [(0,1),(1,2)]
    #     TimeStamp: 1     Value: original bounds: (1,2) actual bounds: (1,2) observations: [(1,2),(2,3)]
    #     TimeStamp: 2     Value: original bounds: (2,3) actual bounds: (2,3) observations: [(2,3),(3,4)]
    #     TimeStamp: 3     Value: original bounds: (3,4) actual bounds: (3,4) observations: [(3,4),(4,5)]
    #     TimeStamp: 4     Value: original bounds: (4,5) actual bounds: (4,5) observations: [(4,5),(5,6)]
    #
    #     flatten the segments into a single multi-time-series
    #
    #     >>> mts = ts_sliding.flatten()
    #     >>> mts
    #     0 time series
    #     ------------------------------
    #     TimeStamp: 0     Value: 1
    #     TimeStamp: 1     Value: 2
    #     1 time series
    #     ------------------------------
    #     TimeStamp: 1     Value: 2
    #     TimeStamp: 2     Value: 3
    #     2 time series
    #     ------------------------------
    #     TimeStamp: 2     Value: 3
    #     TimeStamp: 3     Value: 4
    #     3 time series
    #     ------------------------------
    #     TimeStamp: 3     Value: 4
    #     TimeStamp: 4     Value: 5
    #     4 time series
    #     ------------------------------
    #     TimeStamp: 4     Value: 5
    #     TimeStamp: 5     Value: 6
    #     """
    #     if key_func is None:
    #         return MultiTimeSeries(
    #             self._tsc,
    #             self._j_segment_ts.flatten()
    #         )
    #     else:
    #         return MultiTimeSeries(
    #             self._tsc,
    #             self._j_segment_ts.flatten(utils.SegmentUnaryMapFunction(self._tsc, key_func))
    #         )
