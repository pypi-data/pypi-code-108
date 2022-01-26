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

from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSet import FrequentItemSet


class FrequentItemSetModel:
    """
    A frequent item-set model generated from the itemset_mining package in sparkautoai_ts_libs.deps.tspy

    Attributes
    ----------
    min_support : float
        minimum support for fp-growth (between 0 and 1)
    item_set_matcher : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.ItemSetMatcher.ItemSetMatcher`
        the matcher function used in generating this model
    creation_date : str
        time of creation of model
    metadata : str
        any metadata to be stored with model
    frequent_item_sets : list of :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSet.FrequentItemSet`
        a list of all the FIM created itemsets
    """

    def __init__(self, tsc, j_model):
        self._tsc = tsc
        self._j_model = j_model
        fis_list = []
        for fis in self._j_model.frequentItemSets():
            fis_list.append(FrequentItemSet(fis))
        self._fis_list = fis_list

    @property
    def min_support(self):
        """
        Returns
        -------
        float
            minimum support for fp-growth
        """
        return self._j_model.minSupport()

    @property
    def item_set_matcher(self):
        """
        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.ItemSetMatcher.ItemSetMatcher`
            the item-set matcher used in generating this model
        """
        # todo make this python-like
        return self._j_model.itemSetMatcher()

    @property
    def creation_date(self):
        """
        Returns
        -------
        str
            the time of creation of this model
        """
        return self._j_model.creationDate().toString()

    @property
    def frequent_item_sets(self):
        """
        Returns
        -------
        list of :class:`autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining.FrequentItemSet.FrequentItemSet`
            a list of all the FIM created itemsets
        """
        return self._fis_list

    def score(self, series):
        """score the given series with the default scoring mechanism. The default scoring mechanism is defined as the
        number of matches over the total number of frequent itemsets

        Parameters
        ----------
        series : :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
            the input realized time-series

        Returns
        -------
        float
             value between 0 and 1.0 that indicate the ratio of the number of matched Item-Sets to the total number of
             Item-Sets in this model.
        """
        return self._j_model.score(series._j_observations)

    def save(self, path):
        """
        saves the model to path
        """
        if isinstance(path, str):
            self._j_model.save(self._tsc._jvm.java.io.FileOutputStream(path))
        else:
            self._j_model.save(path)

    def __str__(self):
        return self._j_model.toString()

    def __getstate__(self):
        j_model_str = self._tsc._jvm.com.ibm.research.time_series.ml.itemset_mining.PythonConnector.serializeFrequentItemSetModel(self._j_model)
        return {'j_model': j_model_str}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        self._tsc = get_or_create()
        self._j_model = self._tsc._jvm.com.ibm.research.time_series.ml.itemset_mining.PythonConnector.deserializeFrequentItemSetModel(d['j_model'])
        fis_list = []
        for fis in self._j_model.frequentItemSets():
            fis_list.append(FrequentItemSet(fis))
        self._fis_list = fis_list

