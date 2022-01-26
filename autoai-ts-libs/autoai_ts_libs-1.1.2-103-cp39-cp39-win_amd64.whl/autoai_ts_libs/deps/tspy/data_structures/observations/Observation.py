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

from py4j.java_collections import ListConverter, MapConverter
from py4j.java_gateway import JavaObject


class Observation:
    """
    Basic storage unit for a single time-series observation

    .. todo::
        Ask Josh to provide other supported types for `time_tick`

    Attributes
    ----------
    time_tick : int
        the time-tick associated with this observation
    value : any
        the value associated with this observation

    Examples
    --------
    create a simple observation

    >>> import autoai_ts_libs.deps.tspy
    >>> obs = autoai_ts_libs.deps.tspy.observation(1,1)
    >>> obs
    TimeStamp: 1     Value: 1
    """

    def __init__(self, tsc, time_tick=-1, value=None):
        self._tsc = tsc
        self._time_tick = time_tick
        self._value = value

        if type(value) is list:
            j_value = ListConverter().convert(value, self._tsc._gateway._gateway_client)

            self._j_observation = self._tsc._jvm.com.ibm.research.time_series.core.observation.Observation(
                self._time_tick,
                j_value
            )
        elif type(value) is tuple:
            j_value = tsc._jvm.com.ibm.research.time_series.core.utils.Pair(value[0], value[1])

            self._j_observation = self._tsc._jvm.com.ibm.research.time_series.core.observation.Observation(
                self._time_tick,
                j_value
            )
        elif type(value) is dict:
            j_value = MapConverter().convert(value, self._tsc._gateway._gateway_client)

            self._j_observation = self._tsc._jvm.com.ibm.research.time_series.core.observation.Observation(
                self._time_tick,
                j_value
            )
        else:
            self._j_observation = self._tsc._jvm.com.ibm.research.time_series.core.observation.Observation(
                self._time_tick,
                value
            )

    def __call__(self, timestamp, value):
        # self._timestamp = timestamp
        # self._value = value
        #
        # if isinstance(value, list):
        #     j_value = ListConverter().convert(value, self._gateway.gateway_client)
        #
        #     self._j_observation = self._jvm.com.ibm.research.data_structures.core.observation.Observation(
        #         self._timestamp,
        #         j_value
        #     )
        # else:
        #     self._j_observation = self._jvm.com.ibm.research.data_structures.core.observation.Observation(
        #         self._timestamp,
        #         self._value
        #     )
        return Observation(self._tsc, timestamp, value)

    @property
    def time_tick(self):
        """
        Returns
        -------
        int
            the time-tick associated with this observation

        .. todo::
            Ask Josh ...

        """
        return self._time_tick

    @property
    def value(self):
        """
        Returns
        -------
        any
            the value associated with this observation
        """
        return self._value

    def _to_human_readable_str(self, j_trs):
        return self._j_observation.toString(j_trs)

    def __str__(self):
        if self._j_observation is None:
            return ""
        else:
            return self._j_observation.toString()

    def __repr__(self):
        if self._j_observation is None:
            return ""
        else:
            return self._j_observation.toString()

    def __eq__(self, other):
        return self.time_tick is other.time_tick and self.value is other.value
