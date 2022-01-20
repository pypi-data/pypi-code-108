import numpy as np
import scipy.stats as stats


def confidence_interval_mean(series, confidence=0.95):
    n = series.size
    mean = np.mean(series)
    standard_error = series.std()/(n**0.5)
    h = standard_error * stats.t.ppf((1 + confidence) / 2, n - 1)
    return (mean - h, mean + h)

ci_mean = confidence_interval_mean
CI_mean = confidence_interval_mean

def confidence_interval_median(series, level=0.95, bootstrap=5987):
    
    # bootstrap : number of times the confidence intervals around the median should be bootstrapped (percentile method).
    # determine 95% confidence intervals of the median
    
    idx = np.random.randint(series.size, size=(5987, series.size))
    data = series.values[idx]
    medians = np.median(data, axis=1, overwrite_input=True)
    confidence_interval = np.percentile(medians, [(1-level)/0.02, (1+level)/0.02])
    return tuple(confidence_interval)

ci_median = confidence_interval_median
CI_median = confidence_interval_median

def confidence_interval_std(series, level=0.95):
    # SD*SQRT((N-1)/CHISQ.INV(1-(alpha/2), N-1))
    # SD*SQRT((N-1)/CHISQ.INV((alpha/2), N-1))
    pass