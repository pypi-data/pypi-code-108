"""
main entry-point for creation of :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
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

def _empty():
    """creates an empty observation-collection

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        a new observation-collection
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.observations.empty()

def _of(*observations):
    """creates a collection of observations

    Parameters
    ----------
    observations : varargs
        a variable number of observations

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        a new observation-collection
    """
    from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
    tsc = get_or_create()
    return tsc.observations.of(*observations)

def observations(*varargs):
    """returns an :class:`.ObservationCollection`

    Parameters
    ----------
    observations : varargs
        either empty or a variable number of observations

    Returns
    -------
    :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries.BoundTimeSeries`
        a new observation-collection
    """
    if len(varargs) > 0:
        return _of(*varargs)
    else:
        return _empty()
