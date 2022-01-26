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

class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc
        self._jvm = tsc._jvm

    def static_threshold(self, threshold):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.segmentation.SegmentationTransformers.staticThreshold(threshold)

    def static_threshold_with_annotation(self):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.segmentation.SegmentationTransformers.staticThresholdWithAnnotation()

    def dynamic_threshold(self, alpha, factor, threshold):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.segmentation.SegmentationTransformers.dynamicThreshold(
            alpha,
            factor,
            threshold
        )

    def regression(self, max_error, skip, use_relative=False):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.segmentation.SegmentationTransformers.regression(max_error, skip, use_relative)

    def statistical_changepoint(self, min_segment_size=2, threshold=2.0):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.segmentation.SegmentationTransformers.statisticalChangePoint(min_segment_size, threshold)

    def cusum(self, threshold):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.segmentation.SegmentationTransformers.cusum(threshold)

    def record_based_anchor(self, func, left_window_size, right_window_size, perc=1.0, enforce_size=True, include_anchor=True):
        if hasattr(func, '__call__'):
            from autoai_ts_libs.deps.tspy.data_structures import utils
            func = utils.FilterFunction(self._tsc, func)
        else:
            func = self._tsc._jvm.com.ibm.research.time_series.transforms.utils.python.Expressions.toFilterFunction(func)
        return self._jvm.com.ibm.research.time_series.core.core_transforms.segmentation.GenericSegmentationTransformers.segmentByRecordBasedAnchor(
            func,
            left_window_size,
            right_window_size,
            perc,
            enforce_size,
            include_anchor
        )
