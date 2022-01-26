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

from autoai_ts_libs.deps.tspy.data_structures.observations.BoundTimeSeries import BoundTimeSeries


class SequenceMatcher:
    """
    Function which matches an :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.ItemSetSequence.ItemSetSequence` to a :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
    """
    def __init__(self, tsc, j_matcher):
        self._tsc = tsc
        self._j_matcher = j_matcher

    def matches(self, py_itemset_sequence, series):
        """function which given an :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.ItemSetSequence.ItemSetSequence` and a :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`, will determine if they match. If
        they match, the match will be returned

        Parameters
        ----------
        py_itemset_sequence : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.ItemSetSequence.ItemSetSequence`
            sequence of item-sets
        series : :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
            the series to test

        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
            the match as a series
        """
        from py4j.java_collections import JavaList
        if len(series) is not 0 and isinstance(series.first().value, JavaList):
            result = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.functions.PythonListMatcher(
                self._j_matcher, series._j_observations).matches(py_itemset_sequence._j_itemset_sequence)
        else:
            result = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.functions.PythonSingletonMatcher(
                self._j_matcher, series._j_observations).matches(py_itemset_sequence._j_itemset_sequence)
        if result is None:
            return result
        else:
            return BoundTimeSeries(self._tsc, result)
