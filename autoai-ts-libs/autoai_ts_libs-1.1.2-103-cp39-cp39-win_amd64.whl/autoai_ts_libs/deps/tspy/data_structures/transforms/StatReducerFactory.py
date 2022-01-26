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

class Factory(object):

    def __init__(self, jvm):
        self._jvm = jvm

    def adf(self, lag=None, p_value=-3.45):
        if lag is None:
            return self._jvm.com.ibm.research.time_series.transforms.reducers.stats.StatReducers.adf(p_value)
        else:
            return self._jvm.com.ibm.research.time_series.transforms.reducers.stats.StatReducers.adf(lag, p_value)

    def granger(self, lag):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.stats.StatReducers.granger(lag)
