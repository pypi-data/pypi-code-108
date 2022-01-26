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

    def sum(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.sum()

    def average(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.average()

    def correlation(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.correlation()

    def cross_correlation(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.PythonMathReducers.crossCorrelation()

    def auto_correlation(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.PythonMathReducers.autoCorrelation()

    def convolve(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.convolve()

    def fft(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.fft()

    def standard_deviation(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.standardDeviation()

    def skewness(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.skewness()

    def kurtosis(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.kurtosis()

    def min(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.PythonMathReducers.min()

    def max(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.PythonMathReducers.max()

    def percentile(self, quantile):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.percentile(quantile)

    def describe(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.describeNumeric()

    def entropy(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.entropy()

    def distance_variance(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.distanceVariance()

    def distance_covariance(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.distanceCovariance()

    def distance_correlation(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.distanceCorrelation()

    def mutual_information(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.mutualInformation()

    def histogram(self, min, max, num_divisions, normalize=False):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.histogram(min, max, num_divisions, normalize)
    # todo add mutual information criterion object

    def median(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.median()

    def integral(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.integral()

    def cdf(self, min_value, max_value, num_divisions):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.cdf(min_value, max_value, num_divisions)

    def abs_energy(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.absEnergy()

    def abs_sum_of_changes(self):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.absSumOfChanges()

    def c3(self, lag):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.c3(lag)

    def energy_ratio(self, sum_squares):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.energyRatio(sum_squares)

    def regression(self, approximate_intercept=True):
        return self._jvm.com.ibm.research.time_series.transforms.reducers.math.MathReducers.regression(approximate_intercept)

