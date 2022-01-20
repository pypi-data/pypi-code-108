import re
import math
from decimal import Decimal

import numpy as np
import pandas as pd
from scipy.stats import distributions

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import groupby

# boxplot
def _get_boxplot_quantiles(series, whis=1.5):
    # get the matplotlib boxplot quantiles
    # sort of direct copy from the matplotlib library

    q1, median, q3 = np.percentile(series, [25, 50, 75])

    if np.isscalar(whis):
        iqr = q3 - q1
        loval = q1 - (whis * iqr)
        hival = q3 + (whis * iqr)
    else:
        loval, hival = np.percentile(series, sorted(whis))

    # get high extreme
    wiskhi = series[series <= hival]
    if len(wiskhi) == 0 or np.max(wiskhi) < q3:
        high = q3
    else:
        high = np.max(wiskhi)

    # get low extreme
    wisklo = series[series >= loval]
    if len(wisklo) == 0 or np.min(wisklo) > q1:
        low = q1
    else:
        low = np.min(wisklo)
    
    return [low, q1, q3, high]

def _get_boxplot_outliers(series, whis=1.5):
    low, q1, q3, high = _get_boxplot_quantiles(series=series, whis=whis)

    return series[series < low].append(series[series > high]).values


# histogram
def _bins(series, points, min_bins=10, max_bins=20, max_decimals=10):

    if not isinstance(series, pd.Series):
        raise ValueError('series is not a Pandas Series')

    if not isinstance(points, (tuple, list)):
        raise ValueError('points is not a tuple or a list')

    if not isinstance(min_bins, int):
        raise ValueError('min_bins is not an integer')
    else:
        if min_bins < 1:
            min_bins = 1
    
    if not isinstance(max_bins, int):
        raise ValueError('max_bins is not an integer')
    else:
        if max_bins < 5:
            max_bins = 5
    
    
    # decimal places for points
    decimal_places = min(-min([Decimal(str(x)).as_tuple().exponent for x in points]), max_decimals)
    
    gcd_factor = 10**decimal_places
    bin_size = np.gcd.reduce([int(round(x*gcd_factor)) for x in points]) / gcd_factor
    
    # adjust bin_size
    series_range = series.max() - series.min()

    ## min_bins
    range_factor = np.ceil(min_bins/(series_range/bin_size))
    bin_size = bin_size / range_factor
    
    ## max_bins
    range_factor = np.ceil((series_range/bin_size)/max_bins)
    bin_size = bin_size * range_factor

    # new decimal places
    decimal_places = -Decimal(str(bin_size)).as_tuple().exponent
    
    # get start and end
    start = round(series.min() - (series.min() % bin_size), decimal_places)
    end = round(series.max() - (series.max() % bin_size) + bin_size, decimal_places)

    return np.arange(start, end, bin_size)



def _get_nice_list(the_list, max_len=3):
    if len(the_list) == 1:
        return the_list[0]
    elif len(the_list) <= max_len:
        return ", ".join(the_list[:-1])+" and "+the_list[-1]
    else:
        return ", ".join(the_list[:2])+", ... and "+the_list[-1]

def _get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def _get_digits(x, len=6):
    if x > 0:
        prtd = max(len, math.ceil(math.log10(abs(x))))
        prtd -= math.ceil(math.log10(abs(x)))
        prtd = min(len, prtd)
        return prtd
    else:
        return 0
        
def _format_digits(x, len=6, digits=None):
    if digits is not None:
        return f'1.{digits}f'
        
    if isinstance(x, list):
        return _format_digits(max([_get_digits(i, len=len) for i in x if i is not None]), len=diglenits)

    elif x is None:
        return f'1.0f'
    elif x == 0 or not math.isfinite(x):
        return f'1.0f'
    else:
        prtd = max(len, math.ceil(math.log10(abs(x))))
        prtd -= math.ceil(math.log10(abs(x)))
        prtd = min(len, prtd)
        return f'1.{prtd}f'

def _get_h0_equal_means(columns):
    if len(columns) == 1:
        return ''
    elif len(columns) > 4:
        return f'$H_0: \\bar{{X}}_{{{columns[0]}}} = \\bar{{X}}_{{{columns[1]}}} = \\bar{{X}}_{{...}} = \\bar{{X}}_{{{columns[-1]}}}$'
    else:
        result = f'$H_0: \\bar{{X}}_{{{columns[0]}}}$'
        for col in columns[1:]:
            result += f'$ = \\bar{{X}}_{{{col}}}$'
        return result
    
def _get_distribution(dist=None):
    distributions = {
        "norm": "Normal (Gaussian)",
        "alpha": "Alpha",
        "anglit": "Anglit",
        "arcsine": "Arcsine",
        "beta": "Beta",
        "betaprime": "Beta Prime",
        "bradford": "Bradford",
        "burr": "Burr",
        "cauchy": "Cauchy",
        "chi": "Chi",
        "chi2": "Chi-squared",
        "cosine": "Cosine",
        "dgamma": "Double Gamma",
        "dweibull": "Double Weibull",
        "erlang": "Erlang",
        "expon": "Exponential",
        "exponweib": "Exponentiated Weibull",
        "exponpow": "Exponential Power",
        "fatiguelife": "Fatigue Life (Birnbaum-Sanders)",
        "foldcauchy": "Folded Cauchy",
        "f": "F (Snecdor F)",
        "fisk": "Fisk",
        "foldnorm": "Folded Normal",
        "frechet_r": "Frechet Right Sided, Extreme Value Type II",
        "frechet_l": "Frechet Left Sided, Weibull_max",
        "gamma": "Gamma",
        "gausshyper": "Gauss Hypergeometric",
        "genexpon": "Generalized Exponential",
        "genextreme": "Generalized Extreme Value",
        "gengamma": "Generalized gamma",
        "genlogistic": "Generalized Logistic",
        "genpareto": "Generalized Pareto",
        "genhalflogist": "Generalized Half Logistic",
        "gilbrat": "Gilbrat",
        "gompertz": "Gompertz (Truncated Gumbel)",
        "gumbel_l": "Left Sided Gumbel, etc.",
        "gumbel_r": "Right Sided Gumbel",
        "halfcauchy": "Half Cauchy",
        "halflogistic": "Half Logistic",
        "halfnorm": "Half Normal",
        "hypsecant": "Hyperbolic Secant",
        "invgamma": "Inverse Gamma",
        "invnorm": "Inverse Normal",
        "invweibull": "Inverse Weibull",
        "johnsonsb": "Johnson SB",
        "johnsonsu": "Johnson SU",
        "laplace": "Laplace",
        "logistic": "Logistic",
        "loggamma": "Log-Gamma",
        "loglaplace": "Log-Laplace (Log Double Exponential",
        "lognorm": "Log-Normal",
        "lomax": "Lomax (Pareto of the second kind)",
        "maxwell": "Maxwell",
        "mielke": "Mielke's Beta-Kappa",
        "nakagami": "Nakagami",
        "ncx2": "Non-central chi-squared",
        "ncf": "Non-central F",
        "nct": "Non-central Student's T",
        "pareto": "Pareto",
        "powerlaw": "Power-function",
        "powerlognorm": "Power log normal",
        "powernorm": "Power normal",
        "rdist": "R distribution",
        "reciprocal": "Reciprocal",
        "rayleigh": "Rayleigh",
        "rice": "Rice",
        "recipinvgauss": "Reciprocal Inverse Gaussian",
        "semicircular": "Semicircular",
        "t": "Student's T",
        "triang": "Triangular",
        "truncexpon": "Truncated Exponential",
        "truncnorm": "Truncated Normal",
        "tukeylambda": "Tukey-Lambda",
        "uniform": "Uniform",
        "vonmises": "Von-Mises (Circular)",
        "wald": "Wald",
        "weibull_min": "Minimum Weibull (see Frechet)",
        "weibull_max": "Maximum Weibull (see Frechet)",
        "wrapcauchy": "Wrapped Cauchy",
        "ksone": "Kolmogorov-Smirnov one-sided (no st",
        "kstwobign": "Kolmogorov-Smirnov two-sided test for Large N",
    }

    return distributions.get(dist, None)