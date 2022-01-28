import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
import statsmodels.tsa.api as smt


def ADFtest(TS, lag=1, title=None):
    if not isinstance(TS, (pd.core.series.Series,)):
        TS = pd.Series(TS)

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

    print(f'* {title}')
    print(f'[ADF Statistic] : {result[0]}')
    print(f'[p-value] : {result[1]}')
    for key, value in result[4].items():
        print(f'[Critical Values {key} ] : {value}')


    with plt.style.context('ggplot'):
        fig = plt.figure(figsize=(13,20))
        # mpl.rcParams['font.family'] = 'Ubuntu Mono'

        layout = (5, 2); axes = {}
        axes['0,0'] = plt.subplot2grid(layout, (0, 0), colspan=2)
        axes['1,0'] = plt.subplot2grid(layout, (1, 0))
        axes['1,1'] = plt.subplot2grid(layout, (1, 1))
        axes['2,0'] = plt.subplot2grid(layout, (2, 1), colspan=2)
        axes['3,0'] = plt.subplot2grid(layout, (3, 0))
        axes['4,0'] = plt.subplot2grid(layout, (4, 0), colspan=2)
        axes['4,1'] = plt.subplot2grid(layout, (4, 1))

        axes['0,0'].set_title('Time Series')
        axes['1,0'].set_title('Histogram')
        axes['4,0'].set_title('QQ Plot')

        TS.plot(ax=axes['0,0'])
        axes['1,0'].hist(TS)
        pd.plotting.lag_plot(TS, lag=lag, ax=axes['1,1'])
        smt.graphics.plot_acf(TS, ax=axes['2,0'], alpha=0.5)
        smt.graphics.plot_pacf(TS, ax=axes['3,0'], alpha=0.5)
        sm.qqplot(TS, line='s', ax=axes['4,0'])
        stats.probplot(TS, sparams=(TS.mean(), TS.std()), plot=axes['4,1'])

        plt.tight_layout()
        plt.show()

