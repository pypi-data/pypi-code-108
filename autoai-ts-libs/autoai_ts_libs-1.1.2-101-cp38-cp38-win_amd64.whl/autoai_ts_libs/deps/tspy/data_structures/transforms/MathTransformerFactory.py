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

    def z_score_with_annotation(self):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.zscoreWithAnnotation()

    def z_score(self, mean=None, sd=None):
        if mean is None and sd is None:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.zscore()
        elif mean is not None or sd is not None:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.zscore(mean, sd)
        else:
            from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage
            raise TSErrorWithMessage("mean and sd must either both be none or both be specified")

    def difference(self):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.difference()

    def detect_anomalies(self, forecasting_model, confidence, update_model=False, info=False):
        if info:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.detectAnomaliesWithInfo(
                forecasting_model._j_fm,
                confidence,
                update_model
            )
        else:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.detectAnomalies(
                forecasting_model._j_fm,
                confidence,
                update_model
            )

    def awgn(self, mean=None, sd=None):
        if mean is None and sd is None:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.awgn()
        elif sd is None:
            j_sd = self._jvm.java.lang.Double.NaN
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.awgn(mean, j_sd)
        elif mean is None:
            j_mean = self._jvm.java.lang.Double.NaN
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.awgn(j_mean, sd)
        else:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.awgn(mean, sd)

    def mwgn(self, mean=None):
        if mean is None:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.mwgn()
        else:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.mwgn(mean)

    def paa(self, m):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.paa(m)

    def sax(self, min_value, max_value, num_bins):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.sax(min_value, max_value, num_bins)

    def ema(self, smoothing_constant):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.ema(smoothing_constant)

    def decompose(self, samples_per_season, multiplicative):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.PythonMathTransformers.decompose(
            samples_per_season,
            multiplicative
        )

    def discrete_cosine(self):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.discreteCosine()

    def fit_regression(self, periodicity):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.fitRegression(periodicity)

    def min_max_scaler(self, min_value=None, max_value=None):
        if min_value is None and max_value is None:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.minMaxScaler()
        elif min_value is not None or max_value is not None:
            return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.minMaxScaler(min_value, max_value)
        else:
            from autoai_ts_libs.deps.tspy.exceptions import TSErrorWithMessage
            raise TSErrorWithMessage("min_value and max_value must either both be none or both be specified")

    def min_max_scaler_with_annotation(self):
        return self._jvm.com.ibm.research.time_series.transforms.transformers.math.MathTransformers.minMaxScalerWithAnnotation()
