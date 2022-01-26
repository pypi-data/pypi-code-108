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
from autoai_ts_libs.deps.tspy.data_structures import Segment
from autoai_ts_libs.deps.tspy.data_structures.forecasting.Prediction import Prediction


class TSBuilder:
    """
    a mutable builder for creating an :class:`.ObservationCollection`
    """
    def __init__(self, tsc):
        self._tsc = tsc
        self._observations_list = []

    def add(self, observation):
        """adds an observation to the builder

        Parameters
        ----------
        observation : :class:`.Observation`, tuple
            the observation or tuple(time_tick, value) to add

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        if isinstance(observation, tuple):
            if isinstance(observation[1], Segment):
                res = {'timestamp': observation[0], 'segment': self._segment_value_to_json(observation[1])}
            elif isinstance(observation[1], Prediction):
                res = {'timestamp': observation[0], 'prediction': self._prediction_value_to_json(observation[1])}
            else:
                res = {'timestamp': observation[0], 'value': observation[1]}
        else:
            if isinstance(observation.value, Segment):
                res = {'timestamp': observation.time_tick, 'segment': self._segment_value_to_json(observation.value)}
            elif isinstance(observation.value, Prediction):
                res = {
                    'timestamp': observation.time_tick,
                    'prediction': self._prediction_value_to_json(observation.value)
                }
            else:
                res = {'timestamp': observation.time_tick, 'value': observation.value}

        self._observations_list.append(res)
        return self

    def _segment_value_to_json(self, value):
        res = {}
        res['start'] = value.start
        res['end'] = value.end
        res['observations'] = []
        for o in value:
            res['observations'].append({'timestamp': o.time_tick, 'value': o.value})
        return res

    def _prediction_value_to_json(self, value):
        res = {}
        res['value'] = value.value
        res['lower_bound'] = value.lower_bound
        res['upper_bound'] = value.upper_bound
        res['error'] = value.error
        return res

    def __len__(self):
        return len(self._observations_list)

    def result(self, granularity=None, start_time=None):
        """
        get an observation-collection from the observations in this builder

        Parameters
        ----------
        granularity : datetime.timedelta, optional
            the granularity for use in time-series :class:`~autoai_ts_libs.deps.tspy.data_structures.observations.TRS.TRS` (default is None if no start_time, otherwise 1ms)
        start_time : datetime, optional
            the starting date-time of the time-series (default is None if no granularity, otherwise 1970-01-01 UTC)

        Returns
        -------
        :class:`.ObservationCollection`
            a new observation-collection
        """
        if granularity is None and start_time is None:
            j_trs = None
        else:
            import datetime
            from autoai_ts_libs.deps.tspy.data_structures.observations.TRS import TRS
            if granularity is None:
                granularity = datetime.timedelta(milliseconds=1)
            if start_time is None:
                start_time = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
            j_trs = TRS(self._tsc, granularity, start_time)

        from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries
        import json
        json_str = json.dumps(self._observations_list)
        j_observations = self._tsc._jvm.com.ibm.research.time_series.core.utils.PythonConnector.createObservationCollectionFromJson(
            json_str,
            j_trs
        )
        return BoundTimeSeries(self._tsc, j_observations)


    def clear(self):
        """
        clear the observations in this builder

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        self._observations_list.clear()
        return self

    def is_empty(self):
        """checks if there is any observation

        Returns
        -------
        bool
            True if no observations exist in this builder, otherwise false
        """
        return len(self._observations_list) == 0

    def add_all(self, observations):
        """
        add all observations in an observation-collection to this builder

        Parameters
        ----------
        observations : :class:`.ObservationCollection` or list
            the observations or list of tuple(time_tick, value) to add

        Returns
        -------
        :class:`~autoai_ts_libs.deps.tspy.utils.TSBuilder.TSBuilder`
            this TSBuilder
        """
        from autoai_ts_libs.deps.tspy.data_structures import Observation
        if isinstance(observations[0], Observation):
            for o in observations:
                self.add(o)
        else:
            for o in observations:
                self.add((o[0], o[1]))

        return self
