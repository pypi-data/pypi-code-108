class randomvar:
    def __init__(self, expectation, dist="normal", variance=0, vmin="unset",
                 vmax="unset", isinteger=False, meanconv=False, length=1):
        self.expectation = expectation
        self.variance = variance
        self.distribution = dist
        self.isinteger = isinteger
        self.meanconv = meanconv
        self.lower = vmin
        self.upper = vmax
        self.diagnosis = "ok"
        self.len = length

    def __str__(self):
        """ This is what is printed if the print method is executed on an
        instance of randomclass: it's defined as it is so that when
        AutoFeedback prints out the expected value of a given variable we get
        something other than '<AutoFeedback.randomclass.randomvar>'"""

        return f"{self.distribution} random variable between {str(self.lower)} \
and {str(self.upper)} with expectation {str(self.expectation)}"

    def __len__(self):
        """ This is what is returned if the len method is executed on an
        instance of randomclass. The expected length (number of elements in an
        array containing random values) is set upon instantiation with the
        optional length parameter which defaults to 1"""
        return self.len

    def _check_for_bad_value(self, val, num):
        if num < 0:
            isint = self.isinteger
        else:
            isint = self.isinteger[num]
        if isint:
            from math import isclose
            if not isclose(val, round(val), abs_tol=10**-7):
                self.diagnosis = "integer"
                return(False)

        if self.lower == "unset" and self.upper == "unset":
            return(True)
        low, up = self.lower, self.upper
        if self.lower != "unset" and num >= 0:
            low = self.lower[num]
        if self.upper != "unset" and num >= 0:
            up = self.upper[num]

        if self.lower == "unset" and val > up:
            self.diagnosis = "range"
            return(False)
        elif self.lower == "unset":
            return(True)
        if val < low and self.upper == "unset":
            self.diagnosis = "range"
            return(False)
        elif self.upper == "unset":
            return(True)
        if val < low or val > up:
            self.diagnosis = "range"
            return(False)
        return(True)

    def _get_statistic(self, value, expectation, variance, number):
        if self.distribution == "normal":
            from math import sqrt
            return (value - expectation) / sqrt(variance/number)
        elif self.distribution == "chi2":
            return (number-1)*value / variance
        return 1

    def _hypo_check(self, stat, number):
        if self.distribution == "normal" or self.distribution == "chi2":
            from AutoFeedback.utils import check_module
            check_module("scipy")
        if self.distribution == "normal":
            from scipy.stats import norm
            if stat > 0:
                pval = 2*norm.cdf(-stat)
            else:
                pval = 2*norm.cdf(stat)
        elif self.distribution == "chi2":
            from scipy.stats import chi2
            pval = chi2.cdf(stat, number-1)
            if pval > 0.5:
                pval = 1-chi2.cdf(stat, number-1)
        else:
            return(False)

        if pval < 0.01:
            self.diagnosis = "hypothesis"
            return(False)
        self.diagnosis = "ok"
        return(True)

    def check_value(self, val):
        if hasattr(self.expectation, "__len__"):
            if len(val) != len(self.expectation):
                self.diagnosis = "number"
                return(False)
            for n, v in enumerate(val):
                if not self._check_random_var(v, n):
                    return(False)
            return(True)
        else:
            return self._check_random_var(val, -1)

    def _check_random_var(self, val, num):
        if hasattr(val, "__len__"):
            for v in val:
                if not self._check_for_bad_value(v, num):
                    return(False)
        elif not self._check_for_bad_value(val, num):
            return(False)
        if hasattr(val, "__len__"):
            if self.meanconv:
                from math import floor
                nn, stride = 0, int(floor(len(val) / 30))
                for vv in val:
                    nn = nn + 1
                    if nn % stride != 0:
                        continue
                    if num < 0:
                        stat = self._get_statistic(
                            vv, self.expectation, self.variance, nn)
                    else:
                        stat = self._get_statistic(
                            vv, self.expectation[num], self.variance[num], nn)
                    if not self._hypo_check(stat, nn):
                        return(False)

                return(True)
            else:
                if num < 0:
                    stat = self._get_statistic(
                        sum(val)/len(val),  self.expectation,
                        self.variance, len(val))
                else:
                    stat = self._get_statistic(
                        sum(val)/len(val), self.expectation[num],
                        self.variance[num],  len(val))
                return self._hypo_check(stat, len(val))
        else:
            if num < 0:
                stat = self._get_statistic(
                    val,  self.expectation, self.variance, 1)
            else:
                stat = self._get_statistic(
                    val,  self.expectation[num], self.variance[num], 1)

        return self._hypo_check(stat, 1)

    def get_error(self, obj):
        error_message = ""
        if self.diagnosis == "integer":
            error_message = "The " + obj + " should only take integer values" + """
             You should be generating integer valued discrete random variables
             Your random variables should thus only ever take integer values
             """
        elif self.diagnosis == "range":
            error_message = "The " + obj + \
                " fall outside the allowed range of values for this\
                type of random variable"
            if self.lower == "unset":
                error_message += "\n The random variable should be less\
                    than or equal to " + \
                    str(self.upper)
            elif self.upper == "unset":
                error_message += "\n The random variable should be greater\
                    than or equal to " + \
                    str(self.lower)
            else:
                error_message += "\n The random variable should be between " +\
                    str(self.lower) + " and " + str(self.upper)
        elif self.diagnosis == "hypothesis":
            error_message = "The " + obj + " appear to be sampled from the wrong distribution" + """
            To test if you generating a random variable from the correct
            distribution the test code performs a hypothesis test.  The null
            hypothesis in this test is that you are sampling from the desired
            distribution and the alternative is that you are not sampling the
            correct distribution.  The size of the critical region is
            determined using a a significance level of 1%.  There is thus a
            small probability that you will fail on this test even if your code
            is correct. If you see this error only you should thus run the
            calculation again to check whether the hypothesis test is giving a
            type I error.  If you fail this test twice your code is most likely
            wrong.
            """
        elif self.diagnosis == "number":
            error_message = "The " + obj + " is not generating the correct number of random variables" + """
            You should be generating a vector that contains multiple random
            variables in this object
            """
        return(error_message)
