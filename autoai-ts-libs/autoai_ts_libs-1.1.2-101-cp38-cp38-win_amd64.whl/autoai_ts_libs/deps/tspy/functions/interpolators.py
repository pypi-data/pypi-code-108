"""
main entry point for time-series interpolators
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

def linear(fill_value=None, history_size=1, future_size=1):
    """fill null value with the value derived using linear interpolation (using a few values in the left and a few values in the right)"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.linear(fill_value, history_size, future_size)


def cubic(fill_value=None, history_size=1, future_size=1):
    """fill null value with the value derived using cubic interpolation (using a few values in the left and a few values in the right)"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.cubic(fill_value, history_size, future_size)


def next(default_value=None):
    """fill null value with the next value, and if there is none, get `default_value`"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.next(default_value)


def prev(default_value=None):
    """fill null value with the previous value, and if there is none, get `default_value`"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.prev(default_value)


def nearest(default_value=None):
    """fill null value with the nearest value, and if there is none, get `default_value`"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.nearest(default_value)


def fill(value):
    """fill null value with the given `value`"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.fill(value)


def nullify():
    """set the given data to null value"""
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.interpolators.nullify()
