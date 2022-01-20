from scipy import stats
import statsmodels.tsa.api as smt


def ADFTest(TS):
    """
    Augmented Dickey-Fuller test

    Null Hypothesis (H0): [if p-value > 0.5, non-stationary]
    >   Fail to reject, it suggests the time series has a unit root, meaning it is non-stationary.
    >   It has some time dependent structure.
    Alternate Hypothesis (H1): [if p-value =< 0.5, stationary]
    >   The null hypothesis is rejected; it suggests the time series does not have a unit root, meaning it is stationary.
    >   It does not have time-dependent structure.
    """
    result = smt.adfuller(TS)
    print('* Augmented Dickey-Fuller Test')
    p = result[1]
    alpha = 0.05
    if p > alpha:
        print(f'p-value:{round(p,4)}|non-stationary (fail to reject H0)')
    else:
        print(f'p-value:{round(p,4)}|stationary (reject H0)')

    print(f'- ADF Statistic : {result[0]}')
    for key, value in result[4].items():
        print(f'  - Critical Values {key} : {value}')


def LagCorrelationTest(TS, lag=1):
    data1 = TS[lag:].values
    data2 = TS.shift(lag).dropna().values

    # calculate Pearson's correlation
    corr, p = stats.pearsonr(data1, data2)
    # display the correlation
    print('\n* Pearsons correlation: %.3f'%corr)

    # interpret the significance
    alpha = 0.05
    if p > alpha:
        print(f'p-value:{round(p,4)}|At lag {lag}, No correlation (fail to reject H0)')
    else:
        print(f'p-value:{round(p,4)}|At lag {lag}, Some correlation (reject H0)')

