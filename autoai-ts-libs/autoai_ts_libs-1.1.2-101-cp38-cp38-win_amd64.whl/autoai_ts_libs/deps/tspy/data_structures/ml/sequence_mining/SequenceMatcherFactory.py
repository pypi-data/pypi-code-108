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

from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining.SequenceMatcher import SequenceMatcher


class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc

    def seq(self):
        return SequenceMatcher(self._tsc, self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.functions.SequenceMatchers.seq())

    def subseq(self, threshold=0.0, matcher_threshold="PS"):
        if matcher_threshold.lower() == "ps":
            j_mt = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.containers.MatcherThreshold.PS
        elif matcher_threshold.lower() == "pm":
            j_mt = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.containers.MatcherThreshold.PM
        elif matcher_threshold.lower() == "ms":
            j_mt = self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.containers.MatcherThreshold.MS
        else:
            raise Exception("must be one of ps, pm, ms")
        return SequenceMatcher(self._tsc, self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.functions.SequenceMatchers.subseq(threshold, j_mt))

    def sublist(self, threshold=0.0):
        return SequenceMatcher(self._tsc, self._tsc._jvm.com.ibm.research.time_series.ml.sequence_mining.functions.SequenceMatchers.sublist(threshold))
