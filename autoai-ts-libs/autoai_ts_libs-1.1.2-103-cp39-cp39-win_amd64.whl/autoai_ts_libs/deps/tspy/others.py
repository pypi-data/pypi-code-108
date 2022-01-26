
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

def observation(time_tick, value):
    """
    create an observation

    Parameters
    ----------
    time_tick : int
        observations time-tick
    value : any
        observations value

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.Observation.Observation`
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.observation(time_tick, value)

def record(**kwargs):
    """OLD API, replace with regular python dict
    create a record type (similar to dict)

    Parameters
    ----------
    kwargs : named args
        key/value arguments

    Returns
    -------
    record
        a dict-like structure that is handled for high performance in time-series
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.record(**kwargs)

def builder():
    """
    create a time-series builder

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TSBuilder.TSBuilder`
        a new time-series builder
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.observations.builder()
