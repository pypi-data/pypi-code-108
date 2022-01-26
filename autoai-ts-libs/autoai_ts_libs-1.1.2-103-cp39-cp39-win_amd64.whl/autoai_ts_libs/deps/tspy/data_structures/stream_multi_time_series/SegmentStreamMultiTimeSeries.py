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

from autoai_ts_libs.deps.tspy.data_structures.stream_multi_time_series.StreamMultiTimeSeries import StreamMultiTimeSeries


class SegmentStreamMultiTimeSeries(StreamMultiTimeSeries):
    """
    A special form of stream-multi-time-series that consists of observations with a value of type
    :class:`~autoai_ts_libs.deps.tspy.data_structures.Segment.Segment`
    """
    def __init__(self, tsc, j_stream_mts, trs=None):
        super().__init__(tsc, j_stream_mts, trs)
        self._tsc = tsc
        self._j_segment_ts = j_stream_mts

    def transform(self, reducer):
        """
        transform this stream-multi-time-series of segments into a stream-multi-time-series of values

        Parameters
        ----------
        reducer : reducer transform
            a reducer transform as seen in :class:`~autoai_ts_libs.deps.tspy.functions.reducers`

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.StreamMultiTimeSeries.StreamMultiTimeSeries`
            a new stream-multi-time-series

        Notes
        -----
        Because this observation values are of segment type, a reducer will be used (transform from segment to value)
        """
        if isinstance(reducer, dict):
            from py4j.java_collections import MapConverter
            reducer = MapConverter().convert(reducer, self._tsc._gateway._gateway_client)

        return StreamMultiTimeSeries(
            self._tsc,
            self._j_stream_mts.transform(reducer),
            self._trs
        )

    def filter(self, func):
        if hasattr(func, '__call__'):
            from autoai_ts_libs.deps.tspy.data_structures import utils
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)

        return SegmentStreamMultiTimeSeries(
            self._tsc,
            self._j_segment_ts.filter(func),
            self._trs
        )

    def transform_segments(self, transform):
        """
        produce a new segment-stream-multi-time-series where each segment is transformed to a new segment using a unary
        transform

        Parameters
        ----------
        transform : UnaryTransform
            the transformation to apply on each segment of this segment-stream-multi-time-series

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.SegmentStreamMultiTimeSeries.SegmentStreamMultiTimeSeries`
            a new segment-stream-multi-time-series
        """
        return SegmentStreamMultiTimeSeries(
            self._tsc,
            self._j_segment_ts.transformSegments(transform),
            self._trs
        )
