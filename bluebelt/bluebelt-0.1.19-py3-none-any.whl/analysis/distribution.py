import pandas as pd
import numpy as np
import scipy.stats as stats
import math

from bluebelt.helpers.testresults import TestResults


def anderson_darling(frame, dist='norm', alpha=0.05):


    # check for dataframe and columns
    if isinstance(frame, pd.Series):
        frame = pd.DataFrame(frame)
    elif isinstance(frame, pd.DataFrame):
        if isinstance(columns, list):
            frame = frame[columns]
    else:
        raise InputError('the input is not a Pandas Series or DataFrame')
    
    pvalue_overall = 1
    statistic = 0
    
    for col in frame.columns:
        AD, critical_values, significance_level = stats.anderson(frame[col].dropna().values, dist=dist)
        AD_adjusted = AD*(1 + (.75/50) + 2.25/(50**2))
        if AD_adjusted >= .6:
            pvalue = math.exp(1.2937 - 5.709*AD_adjusted - .0186*(AD_adjusted**2))
        elif AD_adjusted >=.34:
            pvalue = math.exp(.9177 - 4.279*AD_adjusted - 1.38*(AD_adjusted**2))
        elif AD_adjusted >.2:
            pvalue = 1 - math.exp(-8.318 + 42.796*AD_adjusted - 59.938*(AD_adjusted**2))
        else:
            pvalue = 1 - math.exp(-13.436 + 101.14*AD_adjusted - 223.73*(AD_adjusted**2))

        if pvalue < pvalue_overall:
            pvalue_overall = pvalue
            statistic = AD

    passed = True if pvalue_overall >= alpha else False
    
    description = f'Anderson-Darling test results for: {", ".join([str(col) for col in frame.columns])}'

    description += f'\np-value:'.ljust(12)+f'{pvalue_overall:1.4f}'
    description += f'\nstatistic:'.ljust(12)+f'{statistic:1.2f}'

    return TestResults(name=f'Distribution Test ({dist})', test='Anderson-Darling', statistic=statistic, pvalue=pvalue_overall, passed=passed, description=description)


def normal_distribution(frame, columns=None, alpha=0.05):
    """
    D’Agostino-Pearson test
    
    null hypothesis: x comes from a normal distribution
    
    test all pandas dataframe columns for normal distribution
    input pivoted dataframe
    Returns the scipy NormaltestResult; statistic, pvalue for a single column
    Returns the worst scipy NormaltestResult as a tuple; statistic, pvalue for multiple columns
    pvalue >= 0.05 : column values are (all) normally distributed
    pvalue < 0.05: column values are not (all) normally distributed
    """

    # check for dataframe and columns
    if isinstance(frame, pd.Series):
        frame = pd.DataFrame(frame)
    elif isinstance(frame, pd.DataFrame):
        if isinstance(columns, list):
            frame = frame[columns]
    else:
        raise InputError('the input is not a Pandas Series or DataFrame')
    
    pvalue = 1
    statistic = 0
    
    for col in frame.columns:
        result = stats.normaltest(frame[col].dropna().values)
        if result.pvalue < pvalue:
            pvalue = result.pvalue
            statistic = result.statistic

    passed = True if pvalue >= alpha else False
    
    description = f'Normal Distribution test results for: {", ".join([str(col) for col in frame.columns])}'
    description += f'\npvalue:'.ljust(12)+f'{pvalue:1.4f}'
    description += f'\nstatistic:'.ljust(12)+f'{statistic:1.4f}'
    
    return TestResults(name='Normal Distribution', test="D'Agostino-Pearson", statistic=result.statistic, pvalue=result.pvalue, passed=passed, description=description)

dagostino_pearson = normal_distribution