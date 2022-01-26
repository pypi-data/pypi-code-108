from py4j.java_collections import MapConverter

from autoai_ts_libs.deps.tspy.data_structures import utils
from autoai_ts_libs.deps.tspy.data_structures.observations.BoundMultiTimeSeries import BoundMultiTimeSeries


class BoundSegmentMultiTimeSeries(BoundMultiTimeSeries):

    def __init__(self, tsc, j_bound_mts):
        super().__init__(tsc, j_bound_mts)
        self._tsc = tsc
        self._j_bound_mts = j_bound_mts

    def add_segment_annotation(self, key, annotation_reducer):
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.addSegmentAnnotation(key, annotation_reducer))

    def transform_segments(self, unary_transform, annotation_mapper=None):
        if annotation_mapper is None:
            return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.transformSegments(unary_transform))
        else:
            j_annotation_mapper = MapConverter().convert(annotation_mapper, self._tsc._gateway._gateway_client)
            return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.transformSegments(unary_transform,
                                                                                            j_annotation_mapper))

    def filter(self, func):
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.filter(utils.FilterFunction(self._tsc, func)))

    def map_segments(self, func):
        return BoundSegmentMultiTimeSeries(self._tsc, self._j_bound_mts.mapSegments(utils.BinaryMapFunction(self._tsc, func)))

    def flatten(self, key_func=None):
        if key_func is None:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.flatten()
            )
        else:
            return BoundSegmentMultiTimeSeries(
                self._tsc,
                self._j_bound_mts.flatten(utils.SegmentUnaryMapFunction(self._tsc, key_func))
            )
