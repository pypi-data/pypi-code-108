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

from autoai_ts_libs.deps.tspy.data_structures.observations.Observation import Observation
from autoai_ts_libs.deps.tspy.data_structures import utils


class ObservationStream:
    """
    A queue of observations that can be accessed in a streaming manner
    """

    def __init__(self, tsc, j_observation_stream):
        self._tsc = tsc
        self._j_observation_stream = j_observation_stream
        self._obj_type = None

    def __iter__(self):
        j_iter = self._j_observation_stream.iterator()
        while True:
            j_obs = j_iter.next()
            py_obj, obj_type = utils.cast_to_py_if_necessary(self._tsc, j_obs.getValue(), self._obj_type)
            self._obj_type = obj_type
            yield Observation(self._tsc, j_obs.getTimeTick(), py_obj)

    def __next__(self):
        j_obs = self._j_observation_stream.poll()
        py_obj, obj_type = utils.cast_to_py_if_necessary(self._tsc, j_obs.getValue(), self._obj_type)
        self._obj_type = obj_type
        return Observation(self._tsc, j_obs.getTimeTick(), py_obj)

    def poll(self, polling_interval=1000):
        """
        Poll with blocking for the most recent observation and remove that observation from the queue. If no observation
        exists, poll will be called every polling_interval milliseconds.

        Parameters
        ----------
        polling_interval : int, optional
            how often to check for a new Observation til one is returned (default is 1000)

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
            the next observation
        """
        j_obs = self._j_observation_stream.poll(polling_interval)
        py_obj, obj_type = utils.cast_to_py_if_necessary(self._tsc, j_obs.getValue(), self._obj_type)
        self._obj_type = obj_type
        return Observation(self._tsc, j_obs.getTimeTick(), py_obj)

    def peek(self):
        """
        Peek with non-blocking for the most recent observation. If no observation exists, return None.

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.time_series.Observation.Observation`
            the next observation
        """
        j_opt_obs = self._j_observation_stream.peek()
        if j_opt_obs.isPresent():
            j_obs = j_opt_obs.get()
            py_obj, obj_type = utils.cast_to_py_if_necessary(self._tsc, j_obs.getValue(), self._obj_type)
            self._obj_type = obj_type
            return Observation(self._tsc, j_obs.getTimeTick(), py_obj)
        else:
            return None
