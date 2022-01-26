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

from autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries import StreamTimeSeries


class SegmentStreamTimeSeries(StreamTimeSeries):
    """
    A special form of stream-time-series that consists of observations with a value of type
    :class:`~autoai_ts_libs.deps.tspy.data_structures.Segment.Segment`
    """
    def __init__(self, tsc, j_stream_time_series, trs=None):
        super().__init__(tsc, j_stream_time_series, trs)
        self._tsc = tsc
        self._j_segment_ts = j_stream_time_series

    def transform(self, reducer):
        """
        transform this stream-time-series of segments into a stream-time-series of values

        Parameters
        ----------
        reducer : reducer transform
            a reducer transform as seen in :class:`~autoai_ts_libs.deps.tspy.functions.reducers`

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.data_structures.stream_time_series.StreamTimeSeries.StreamTimeSeries`
            a new stream-time-series

        Notes
        -----
        Because this observation values are of segment type, a reducer will be used (transform from segment to value)
        """
        return StreamTimeSeries(
            self._tsc,
            self._j_stream_time_series.transform(reducer),
            self._trs
        )

    def filter(self, func):
        if hasattr(func, '__call__'):
            from autoai_ts_libs.deps.tspy.data_structures import utils
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return SegmentStreamTimeSeries(
            self._tsc,
            self._j_stream_time_series.filter(func),
            self._trs
        )

    def transform_segments(self, transform):
        """
        produce a new segment-stream-time-series where each segment is transformed to a new segment using a unary
        transform

        Parameters
        ----------
        transform : UnaryTransform
            the transformation to apply on each segment of this segment-stream-time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.SegmentStreamTimeSeries.SegmentStreamTimeSeries`
            a new segment-stream-time-series
        """
        return SegmentStreamTimeSeries(
            self._tsc,
            self._j_stream_time_series.transformSegments(transform),
            self._trs
        )
