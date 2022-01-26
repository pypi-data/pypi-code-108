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
from autoai_ts_libs.deps.tspy.data_structures import utils


class SegmentMultiTimeSeries(MultiTimeSeries):
    """
    A special form of multi-time-series that consists of observations with a value of type
    :class:`~autoai_ts_libs.deps.tspy.data_structures.Segment.Segment`
    """

    def __init__(self, tsc, j_mts):
        super().__init__(tsc, j_mts)
        self._tsc = tsc
        self._j_segment_mts = j_mts

    # def flatten(self, key_func=None):
    #     """
    #     converts this segment-multi-time-series into a multi-time-series where each time-series will be the result of a
    #     single segment
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
    #     create a simple multi-time-series
    #
    #     >>> import autoai_ts_libs.deps.tspy
    #     >>> mts_orig = autoai_ts_libs.deps.tspy.multi_time_series.dict({'a': autoai_ts_libs.deps.tspy.data_structures.list([1,2,3]), 'b': autoai_ts_libs.deps.tspy.data_structures.list([4,5,6])})
    #     >>> mts_orig
    #     a time series
    #     ------------------------------
    #     TimeStamp: 0     Value: 1
    #     TimeStamp: 1     Value: 2
    #     TimeStamp: 2     Value: 3
    #     b time series
    #     ------------------------------
    #     TimeStamp: 0     Value: 4
    #     TimeStamp: 1     Value: 5
    #     TimeStamp: 2     Value: 6
    #
    #     segment the multi-time-series using a simple sliding window
    #
    #     >>> mts_sliding = mts_orig.segment(2)
    #     >>> mts_sliding
    #     a time series
    #     ------------------------------
    #     TimeStamp: 0     Value: original bounds: (0,1) actual bounds: (0,1) observations: [(0,1),(1,2)]
    #     TimeStamp: 1     Value: original bounds: (1,2) actual bounds: (1,2) observations: [(1,2),(2,3)]
    #     b time series
    #     ------------------------------
    #     TimeStamp: 0     Value: original bounds: (0,1) actual bounds: (0,1) observations: [(0,4),(1,5)]
    #     TimeStamp: 1     Value: original bounds: (1,2) actual bounds: (1,2) observations: [(1,5),(2,6)]
    #
    #     flatten the segments into a single multi-time-series
    #
    #     >>> mts = mts_sliding.flatten()
    #     >>> mts
    #     (a, 0) time series
    #     ------------------------------
    #     TimeStamp: 0     Value: 1
    #     TimeStamp: 1     Value: 2
    #     (b, 0) time series
    #     ------------------------------
    #     TimeStamp: 0     Value: 4
    #     TimeStamp: 1     Value: 5
    #     (a, 1) time series
    #     ------------------------------
    #     TimeStamp: 1     Value: 2
    #     TimeStamp: 2     Value: 3
    #     (b, 1) time series
    #     ------------------------------
    #     TimeStamp: 1     Value: 5
    #     TimeStamp: 2     Value: 6
    #     """
    #     if key_func is None:
    #         return MultiTimeSeries(self._tsc, self._j_segment_mts.flatten())
    #     else:
    #         return MultiTimeSeries(
    #             self._tsc,
    #             self._j_segment_mts.flatten(utils.SegmentUnaryMapFunction(self._tsc, key_func))
    #         )
