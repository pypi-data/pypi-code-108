import pandas as pd
import scipy.stats as stats
from collections import namedtuple

from bluebelt.helpers.testresults import TestResults

def equal_means(frame=None, columns=None, alpha=0.05):
    """
    Test a dataframe for equal means over the dataframe columns.

    frame: a pandas DataFrame
    columns: string or list of strings with the column names to be tested
    alpha: test threshold

    applies ANOVA or Kruskal-Wallis test

    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    
    """

    # check for dataframe and columns
    if not isinstance(frame, pd.DataFrame):
        raise InputError('the frame is not a Pandas DataFrame')

    if isinstance(columns, list):
        if len(columns) > 1:
            frame = frame[columns]
        else:
            raise InputError('to test for equal means we need more than one column in the DataFrame')

    # test for normal distribution; null hypothesis: values come from a normal distribution
    if normal_distribution(frame, alpha).passed and levene(frame, alpha).passed:
        # all columns in the dataframe come from a normal distribution AND have equal variances
        # do Anova
        return anova(frame, alpha)
    else:
        # not all columns in the dataframe come from a normal distribution OR have equal variances
        # do Kruskal-Wallis
        return kruskal(frame, alpha)

def anova(frame=None, columns=None, alpha=0.05):
    """
    apply the one way ANOVA test on a pandas dataframe with the columns as groups to compare
    Returns the scipy F_onewayResult; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """

    # check for dataframe and columns
    if not isinstance(frame, pd.DataFrame):
        raise InputError('the frame is not a Pandas DataFrame')

    if isinstance(columns, list):
        if len(columns) > 1:
            frame = frame[columns]
        else:
            raise InputError('to test for equal means we need more than one column in the DataFrame')

    result = stats.f_oneway(*frame.dropna().T.values)
    passed = True if result.pvalue >= alpha else False

    description = f'One Way Anova test results for {frame.axes[1].name}'
    for field in result._fields:
        description += f'\n{field}:'.ljust(12)+f'{getattr(result, field):1.4f}'

    return TestResults(name='Equal Means', test='One Way ANOVA', statistic=result.statistic, pvalue=result.pvalue, passed=passed, description=description)

def kruskal(frame=None, columns=None, alpha=0.05):
    """
    apply the Kruskal-Wallis test on a pandas dataframe with the columns as groups to compare
    Returns the scipy KruskalResult; statistic, pvalue
    pvalue >= alpha (default 0.05) : columns have equal means
    pvalue < alpha: columns don't have equal means
    """

    # check for dataframe and columns
    if not isinstance(frame, pd.DataFrame):
        raise InputError('the frame is not a Pandas DataFrame')

    if isinstance(columns, list):
        if len(columns) > 1:
            frame = frame[columns]
        else:
            raise InputError('to test for equal means we need more than one column in the DataFrame')

    result = stats.kruskal(*frame.dropna().T.values)
    passed = True if result.pvalue >= alpha else False
    
    description = f'Kruskal-Wallis test results for {frame.axes[1].name}'
    for field in result._fields:
        description += f'\n{field}:'.ljust(12)+f'{getattr(result, field):1.4f}'
    
    return TestResults(name='Equal Means', test='Kruskal-Wallis', statistic=result.statistic, pvalue=result.pvalue, passed=passed, description=description)

def levene(frame=None, columns=None, alpha=0.05):
    """
    apply levene's test on a pandas dataframe with the columns as groups to compare
    Returns the scipy LeveneResult; statistic, pvalue
    pvalue >= 0.05 : columns have equal variances
    pvalue < 0.05: columns don't have equal variances
    """

    # check for dataframe and columns
    if not isinstance(frame, pd.DataFrame):
        raise InputError('the frame is not a Pandas DataFrame')

    if isinstance(columns, list):
        if len(columns) > 1:
            frame = frame[columns]
        else:
            raise InputError('to test for equal variances we need more than one column in the DataFrame')


    result = stats.levene(*frame.dropna().T.values)
    passed = True if result.pvalue >= alpha else False
    
    description = f'Levene\'s test results for {frame.axes[1].name}'
    for field in result._fields:
        description += f'\n{field}:'.ljust(12)+f'{getattr(result, field):1.4f}'
    
    return TestResults(name='Equal Variances', test='Levene\'s Test', statistic=result.statistic, pvalue=result.pvalue, passed=passed, description=description)

