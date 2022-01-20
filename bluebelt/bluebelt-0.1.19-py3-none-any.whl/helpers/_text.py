import re
import math

from scipy.stats import distributions

def get_nice_list(the_list, max_len=3):
    if len(the_list) == 1:
        return the_list[0]
    elif len(the_list) <= max_len:
        return ", ".join(the_list[:-1])+" and "+the_list[-1]
    else:
        return ", ".join(the_list[:2])+", ... and "+the_list[-1]

def get_valid_filename(s):
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)

def get_digits(x, digits=6):
    prtd = max(digits, math.ceil(math.log10(abs(x))))
    prtd -= math.ceil(math.log10(abs(x)))
    prtd = min(digits, prtd)
    return prtd

def format_digits(x, digits=6):
    if isinstance(x, list):
        return format_digits(max([get_digits(i, digits=digits) for i in x if i is not None]), digits=digits)

    elif x is None:
        return 0
    elif x == 0 or not math.isfinite(x):
        return x
    else:
        prtd = max(digits, math.ceil(math.log10(abs(x))))
        prtd -= math.ceil(math.log10(abs(x)))
        prtd = min(digits, prtd)
        return f'1.{prtd}f'

def get_h0_equal_means(columns):
    if len(columns) == 1:
        return ''
    elif len(columns) > 4:
        return f'$H_0: \\bar{{X}}_{{{columns[0]}}} = \\bar{{X}}_{{{columns[1]}}} = \\bar{{X}}_{{...}} = \\bar{{X}}_{{{columns[-1]}}}$'
    else:
        result = f'$H_0: \\bar{{X}}_{{{columns[0]}}}$'
        for col in columns[1:]:
            result += f'$ = \\bar{{X}}_{{{col}}}$'
        return result
    
def get_distribution(dist=None):
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