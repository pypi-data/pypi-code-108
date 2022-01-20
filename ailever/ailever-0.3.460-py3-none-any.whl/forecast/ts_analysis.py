import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.tsa.api as smt
from scipy import stats


class TSA:
    def __init__(self):
        pass

    def stationary(self, TS, title=None):
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
        print()


    def analyze(self, TS, freq=None, lags=None, figsize=(18, 20), style='bmh'):
        if not isinstance(TS, pd.Series):
            TS = pd.Series(TS)

        with plt.style.context(style):
            fig = plt.figure(figsize=figsize)
            # mpl.rcParams['font.family'] = 'Ubuntu Mono'

            layout = (6, 2)
            ts_ax = plt.subplot2grid(layout, (0, 0), colspan=2)
            dc_trend_ax = plt.subplot2grid(layout, (1, 0), colspan=2)
            dc_seasonal_ax = plt.subplot2grid(layout, (2, 0), colspan=2)
            dc_resid_ax = plt.subplot2grid(layout, (3, 0), colspan=2)
            acf_ax = plt.subplot2grid(layout, (4, 0))
            pacf_ax = plt.subplot2grid(layout, (4, 1))
            qq_ax = plt.subplot2grid(layout, (5, 0))
            pp_ax = plt.subplot2grid(layout, (5, 1))


            TS.plot(ax=ts_ax)
            ts_ax.set_title('Time Series')
            decompose = smt.seasonal_decompose(TS, model='additive', freq=freq)
            trend = decompose.trend
            trend.plot(ax=dc_trend_ax)
            dc_trend_ax.set_title('[Decompose] Time Series Trend')
            seasonal = decompose.seasonal
            seasonal.plot(ax=dc_seasonal_ax)
            dc_seasonal_ax.set_title('[Decompose] Time Series Seasonal')
            resid = decompose.resid
            resid.plot(ax=dc_resid_ax)
            dc_resid_ax.set_title('[Decompose] Time Series Resid')
            smt.graphics.plot_acf(TS, lags=lags, ax=acf_ax, alpha=0.5)
            smt.graphics.plot_pacf(TS, lags=lags, ax=pacf_ax, alpha=0.5)

            sm.qqplot(resid, line='s', ax=qq_ax)
            qq_ax.set_title('QQ Plot')
            stats.probplot(resid, sparams=(resid.mean(), resid.std()), plot=pp_ax)

            plt.tight_layout()
            plt.savefig('time_series_analysis.png')
            plt.show()

            return trend, seasonal, resid

    def predict(self):
        pass
