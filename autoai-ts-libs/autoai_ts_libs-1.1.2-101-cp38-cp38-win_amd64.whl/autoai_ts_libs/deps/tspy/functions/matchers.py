"""
main entry point for all sequence and item-set matchers
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

def subset(threshold=0.0, matcher_threshold="PS"):
    """Creates a matcher that matches an array of string values (the pattern) with a string time series, regardless of the
    order in which the items in the pattern occur in the time series.

    Parameters
    ----------
    threshold : float, optional
        indicates the minimum ratio by matcher_threshold type. (default is 0.0)
    matcher_threshold : str, optional
        the threshold type, one of PS (pattern / sequence), PM (pattern / match), MS (match / sequence). (default is PS)

    Returns
    -------
    matcher
        a new matcher
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.ml.ism.item_set_matchers.subset(threshold, matcher_threshold)

def seq():
    """Creates a matcher that matches an array of string values (the pattern) with an entire string time series exactly
    and in sequence

    Returns
    -------
    matcher
        a new matcher
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.ml.ssm.sequence_matchers.seq()


def subseq(threshold=0.0, matcher_threshold="PS"):
    """Creates a matcher that matches an array of string values (the pattern) with a sub-sequence of a string time
    series, to within the specified coverage threshold.

    Parameters
    ----------
    threshold : float, optional
        indicates the minimum ratio by matcher_threshold type. (default is 0.0)
    matcher_threshold : str, optional
        the threshold type, one of PS (pattern / sequence), PM (pattern / match), MS (match / sequence). (default is PS)

    Returns
    -------
    matcher
        a new matcher
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.ml.ssm.sequence_matchers.subseq(threshold, matcher_threshold)


def sublist(threshold=0.0):
    """Creates a matcher that matches an array of string values (the pattern) with a sublist of a string time series, to
    within the specified coverage threshold.

    Parameters
    ----------
    threshold : float, optional
        indicates the minimum ratio by matcher_threshold type. (default is 0.0)

    Returns
    -------
    matcher
        a new matcher
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.ml.ssm.sequence_matchers.sublist(threshold)
