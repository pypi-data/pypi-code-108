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

from autoai_ts_libs.deps.tspy.data_structures.ml.clustering import ClusteringFactory
from autoai_ts_libs.deps.tspy.data_structures.ml.itemset_mining import ISMFactory
from autoai_ts_libs.deps.tspy.data_structures.ml.sequence_mining import SSMFactory


class Factory(object):

    def __init__(self, tsc):
        self._tsc = tsc

    @property
    def ssm(self):
        return SSMFactory.Factory(self._tsc)

    @property
    def ism(self):
        return ISMFactory.Factory(self._tsc)

    @property
    def clustering(self):
        return ClusteringFactory.Factory(self._tsc)
