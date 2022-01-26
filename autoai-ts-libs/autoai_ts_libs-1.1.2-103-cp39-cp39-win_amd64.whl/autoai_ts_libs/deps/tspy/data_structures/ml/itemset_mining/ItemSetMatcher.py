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


class ItemSetMatcher:
    """
    Matcher function for itemset where given an itemset and a time-series, if the itemset matches in the
    time-series, return a time series, otherwise if there is no match, return None
    """
    def __init__(self, tsc, j_matcher):
        self._tsc = tsc
        self._j_matcher = j_matcher

    def matches(self, itemset, py_series):
        """finds the matching between itemset and observation-collection

        Parameters
        ----------
        itemset : list
            the itemset
        py_series : :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
            the series

        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
            a time series, otherwise if there is no match, return None
        """
        from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSet import FrequentItemSet
        if isinstance(itemset, FrequentItemSet):
            result = self._j_matcher.matches(itemset._j_fis.itemSet(), py_series._j_observations)
        else:
            result = self._j_matcher.matches(itemset._j_dis.itemSet(), py_series._j_observations)
        if result is None:
            return result
        else:
            return BoundTimeSeries(self._tsc, result)
