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

from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequence import FrequentSubSequence
from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.SequenceMatcher import SequenceMatcher


class FrequentSubSequenceModel:
    """
    A frequent sub-sequence model generated from the frequent_sequence_mining package in sparkautoai_ts_libs.deps.tspy

    Attributes
    ----------

    min_support : float
        minimum support for prefixspan (between 0 and 1)
    creation_date : str
        time of creation of model
    metadata : str
        any metadata to be stored with model
    frequent_sub_sequences : list of :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequence.FrequentSubSequence`
        a list of all the FSM created subsequences
    sequence_matcher : :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.SequenceMatcher.SequenceMatcher`
        the matcher used for generating this DSM model
    """

    def __init__(self, tsc, j_model):
        self._tsc = tsc
        self._j_model = j_model
        fss_list = []
        for fss in self._j_model.frequentSubSequences():
            fss_list.append(FrequentSubSequence(fss))
        self._fss_list = fss_list

    @property
    def min_support(self):
        """
        Returns
        -------
        float
            the min support for prefixspan when creating this model
        """
        return self._j_model.minSupport()

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
    def metadata(self):
        """
        Returns
        -------
        str
            the metadata stored with this model
        """
        return self._j_model.metadata()

    @property
    def frequent_sub_sequences(self):
        """
        Returns
        -------
        list
            the list of :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.FrequentSubSequence.FrequentSubSequence` generated from the FSM algorithm
        """
        return self._fss_list

    @property
    def sequence_matcher(self):
        """
        Returns
        -------
        :class:`autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.SequenceMatcher.SequenceMatcher`
            the sequence matcher used in generating this model
        """
        return SequenceMatcher(self._tsc, self._j_model.sequenceMatcher())

    def save(self, path):
        if isinstance(path, str):
            self._j_model.save(self._tsc._jvm.java.io.FileOutputStream(path))
        else:
            self._j_model.save(path)

    def score(self, series):
        """score the given series with the default scoring mechanism. The default scoring mechanism is defined as the
        number of matches over the total number of frequent sub-sequences

        Parameters
        ----------
        series : :class:`autoai_ts_libs.deps.tspy.data_structures.observations.ObservationCollection.ObservationCollection`
            the input realized time-series
        Returns
        -------
        float
            a number representing the score of a series relative to this model
        """
        return self._j_model.score(series._j_observations)

    def __str__(self):
        return self._j_model.toString()

    def __getstate__(self):
        j_model_str = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.PythonConnector.serializeFrequentSubSequenceModel(self._j_model)
        return {'j_model': j_model_str}

    def __setstate__(self, d):
        from autoai_ts_libs.deps.tspy.data_structures.context import get_or_create
        self._tsc = get_or_create()
        self._j_model = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.PythonConnector.deserializeFrequentSubSequenceModel(d['j_model'])
        fss_list = []
        for fss in self._j_model.frequentSubSequences():
            fss_list.append(FrequentSubSequence(fss))
        self._fss_list = fss_list


