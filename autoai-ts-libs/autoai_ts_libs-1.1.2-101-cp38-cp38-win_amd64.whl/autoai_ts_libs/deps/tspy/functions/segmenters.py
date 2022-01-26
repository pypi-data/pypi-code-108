"""
main entry point for all segmentation transforms (given time-series return new segment-time-series)
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

def static_threshold(threshold=-1):
    """segment the time-series by a static threshold silence period

    Parameters
    ----------
    threshold : int
        the threshold which denotes when a new segment should be created (inter-arrival-time > threshold)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a static-threshold segmentation transform, which applied on a time-series using to_segments will create segments
        based on silence periods
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.static_threshold(threshold)


def static_threshold_with_annotation():
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.static_threshold_with_annotation()


def dynamic_threshold(alpha, factor, threshold):
    """segment the time-series by a dynamic silence period

    Parameters
    ----------
    alpha : float
        denotes how much to weigh more recent inter-arrival-times
    factor: float
        a muliplication factor used to determine a dynamic threshold to denote a new segment
    threshold : int
        the threshold which denotes when a new segment should be created (inter-arrival-time > threshold)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a dynamic-threshold segmentation transform, which applied on a time-series using to_segments will create segments
        based on dynamic silence periods
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.dynamic_threshold(alpha, factor, threshold)


def regression(max_error, skip, use_relative=False):
    """segment the time-series based on a regression model error

    Parameters
    ----------
    max_error : float
        max error threshold
    skip : int
        number of anomalies to allow
    use_relative : bool, optional
        if True, will use the relative error, otherwise uses absolute error (default is absolute error)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a regression segmentation transform, which applied on a time-series using to_segments will create segments
        based on a regression model error
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.regression(max_error, skip, use_relative)


def statistical_changepoint(min_segment_size=2, threshold=2.0):
    """segment the time-series based on a statistical change-point using z-normalization

    Parameters
    ----------
    min_segment_size : int, optional
        minimum size of segment to allow (default is 2)
    threshold : float, optional
        difference threshold to denote change point (default is 2.0)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a statistical change-point segmentation transform, which applied on a time-series using to_segments will create
        segments based on a threshold being exceeded from a z-normalized time-series
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.statistical_changepoint(min_segment_size, threshold)


def cusum(threshold):
    """segment the time-series based on a CUSUM threshold being met

    Parameters
    ----------
    threshold : float
        the threshold which denotes a new segment

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a cumulative-sum segmentation transform, which applied on a time-series using to_segments will create
        segments based on a threshold being exceeded from a CUSUM
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.cusum(threshold)

def record_based_anchor(func, left_window_size, right_window_size, perc=1.0, enforce_size=True, include_anchor=True):
    """segment the time-series based on an anchor with record based window sizes

    Parameters
    ----------
    func : func
        the function to denote an anchor
    left_window_size : int
        number of records to take to the left of the anchor
    right_window_size : int
        number of records to take to the right of the anchor
    perc : float, optional
        approximate percentage of anchor segments to take (default is 1.0)
    enforce_size : bool, optional
        if True, will only keep segments that adhere to a full left_window_size and right_window_size, otherwise will
        remove a segment that is not of full size (default is True)
    include_anchor : boolean, optional
        if True, will include the anchor in the result of the segment, otherwise the anchor will not be part of the
        segment (default is True)

    Returns
    -------
    ~autoai_ts_libs.deps.tspy.data_structures.transforms.UnaryTransform
        a record-based anchor segmentation transform, which applied on a time-series using to_segments will create
        segments based on record-based windows around an anchor point
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.segment_transforms.record_based_anchor(func, left_window_size, right_window_size, perc, enforce_size,
                                                      include_anchor)
