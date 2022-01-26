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

    def augmented_dickey_fuller(self, window, step, lag, p_value):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.stats.StatTransformers.augmentedDickeyFuller(
            window,
            step,
            lag,
            p_value
        )

    def granger_causality(self, window, step, lag):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.stats.StatTransformers.grangerCausality(
            window,
            step,
            lag
        )

    def ljung_box(self, window, step, num_lags, period):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.stats.StatTransformers.ljungBox(
            window,
            step,
            num_lags,
            period
        )
