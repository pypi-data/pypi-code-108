from ._typecore_f import ForecastTypeCaster
from .sarima import Process
from .hypothesis import ADFTest, LagCorrelationTest
from copy import deepcopy
import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.tsa.api as smt
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.vector_ar.vecm import select_order, select_coint_rank
from scipy import stats


dummies = type('dummies', (dict,), {})
class DimensionError(Exception): pass
class TSA:
    r"""
    Examples:
        >>> from ailever.forecast import TSA
        >>> ...
        >>> trendAR=[]; trendMA=[]
        >>> seasonAR=[]; seasonMA=[]
        >>> TSA.sarima((1,1,2), (2,0,1,4), trendAR=trendAR, trendMA=trendMA, seasonAR=seasonAR, seasonMA=seasonMA, n_samples=300)
    """

    @staticmethod
    def sarima(trendparams:tuple=(0,0,0), seasonalparams:tuple=(0,0,0,1), trendAR=None, trendMA=None, seasonAR=None, seasonMA=None, n_samples=300):
        Process(trendparams, seasonalparams, trendAR, trendMA, seasonAR, seasonMA, n_samples)

    def __init__(self, TS, lag=1, select_col=0, visualize=True):
        self.models = dict()
        self.dummies = dummies() 
        self.dummies.__init__ = dict()
        self.dummies.__init__['select_col'] = select_col

        TS = ForecastTypeCaster(TS, outtype='FTC')
        self._TS = TS

        # main univariate forecasting variable
        if TS.array.ndim == 1:
            self.TS = pd.Series(TS.array)
            self.TS.index = pd.RangeIndex(start=0, stop=self.TS.shape[0], step=1)
            #self.TS.index = pd.date_range(end=pd.Timestamp.today().date(), periods=self.TS.shape[0], freq='D')
        elif TS.array.ndim == 2:
            self.TS = pd.Series(TS.array[:,select_col])
            self.TS.index = pd.RangeIndex(start=0, stop=self.TS.shape[0], step=1)
            #self.TS.index = pd.date_range(end=pd.Timestamp.today().date(), periods=self.TS.shape[0], freq='D')
        else:
            raise DimensionError('TSA do not support dimension more than 2.')

        ADFTest(self.TS)
        LagCorrelationTest(self.TS, lag)
        if visualize:
            with plt.style.context('ggplot'):
                plt.figure(figsize=(13,20))
                # mpl.rcParams['font.family'] = 'Ubuntu Mono'

                layout = (5, 2); axes = {}
                axes['0,0'] = plt.subplot2grid(layout, (0, 0), colspan=2)
                axes['1,0'] = plt.subplot2grid(layout, (1, 0))
                axes['1,1'] = plt.subplot2grid(layout, (1, 1))
                axes['2,0'] = plt.subplot2grid(layout, (2, 0), colspan=2)
                axes['3,0'] = plt.subplot2grid(layout, (3, 0), colspan=2)
                axes['4,0'] = plt.subplot2grid(layout, (4, 0))
                axes['4,1'] = plt.subplot2grid(layout, (4, 1))

                axes['0,0'].set_title('Time Series')
                axes['1,0'].set_title('Histogram')
                axes['1,1'].set_title('Lag Plot')
                axes['4,0'].set_title('QQ Plot')

                self.TS.plot(ax=axes['0,0'], marker='o')
                axes['1,0'].hist(self.TS)
                pd.plotting.lag_plot(self.TS, lag=lag, ax=axes['1,1'])
                smt.graphics.plot_acf(self.TS, ax=axes['2,0'], alpha=0.5)
                smt.graphics.plot_pacf(self.TS, ax=axes['3,0'], alpha=0.5)
                sm.qqplot(self.TS, line='s', ax=axes['4,0'])
                stats.probplot(self.TS, sparams=(self.TS.mean(), self.TS.std()), plot=axes['4,1'])

                plt.tight_layout()
                #plt.show()


    def STL(self, steps=1, visualize=True, model='ARIMA',
            seasonal_period=20, resid_transform=True):
        self.dummies.STL = dict()

        # Decompose
        TS = self.TS.values
        result = STL(TS, period=seasonal_period).fit()

        if resid_transform:
            resid = result.resid[np.logical_not(np.isnan(result.resid))]
            si = np.argsort(resid)[::-1]
            sii = np.argsort(np.argsort(resid)[::-1])
            new_resid = np.diff(resid[si])[np.delete(sii, np.argmax(sii))]
            new_resid = np.insert(new_resid, np.argmax(sii), 0)

            origin_resid = deepcopy(result.resid)
            result.resid[np.argwhere(np.logical_not(np.isnan(result.resid))).squeeze()] = new_resid
            result.seasonal[:] = result.seasonal + (origin_resid - result.resid)

        self.dummies.STL['observed'] = result.observed
        self.dummies.STL['trend'] = result.trend
        self.dummies.STL['seasonal'] = result.seasonal
        self.dummies.STL['resid'] = result.resid
        
        # Forecast
        TS = deepcopy(self.TS)
        TS.index = pd.date_range(end=pd.Timestamp.today().date(), periods=TS.shape[0], freq='D')

        if model == 'ARIMA':
            order = (2,1,0)
            model = smt.STLForecast(TS, ARIMA, model_kwargs={'order':order, 'trend':'t'}).fit()
            self.models['STL'] = model

            _summary_frame = model.get_prediction(start=0, end=TS.shape[0]-1+steps).summary_frame(alpha=0.05)
            _summary_frame.index = pd.RangeIndex(start=0, stop=TS.shape[0]+steps, step=1)
            summary_frame = _summary_frame.iloc[order[1]:]
            self.dummies.STL['observed'] = TS
            self.dummies.STL['prediction'] = _summary_frame['mean']
            self.dummies.STL['prediction_lower'] = _summary_frame['mean_ci_lower']
            self.dummies.STL['prediction_upper'] = _summary_frame['mean_ci_upper']

            # VIsualization
            if visualize:
                plt.style.use('ggplot')
                _, axes = plt.subplots(4,1, figsize=(13,15))
                axes[0].fill_between(summary_frame.index,
                                     summary_frame['mean_ci_lower'],
                                     summary_frame['mean_ci_upper'],
                                     color='grey', label='confidence interval')
                axes[0].plot(TS.values, lw=0, marker='o', c='black', label='samples')
                axes[0].plot(summary_frame['mean'], c='red', label='model-forecast')
                axes[0].plot(TS.shape[0]-1+steps, summary_frame['mean'].values[-1], marker='*', markersize=10,  c='red')
                axes[0].axvline(0, ls=':', c='red')
                axes[0].axvline(TS.shape[0]-1, c='red')
                axes[0].axhline(summary_frame['mean'].values[-1], lw=0.5, ls=':', c='gray')
                axes[0].legend()
                axes[1].plot(result.trend, marker='o')
                axes[2].plot(result.seasonal, marker='o')
                axes[3].plot(result.resid, marker='o')
                axes[0].set_title('[Observed]')
                axes[1].set_title('[Trend]')
                axes[2].set_title('[Seasonal]')
                axes[3].set_title('[Resid]')
                plt.tight_layout()
                #plt.show()

        elif model == 'ETS':
            try:
                model = smt.STLForecast(TS, smt.ETSModel, model_kwargs={'error':'mul', 'trend':'add', 'seasonal':'add', 'damped_trend':True, 'seasonal_periods':20}).fit()
            except:
                model = smt.STLForecast(TS, smt.ETSModel, model_kwargs={'error':'add', 'trend':'add', 'seasonal':'add', 'damped_trend':True, 'seasonal_periods':20}).fit()

            self.models['STL'] = model
            summary_frame = model.get_prediction(start=0, end=TS.shape[0]-1+steps).summary_frame(alpha=0.05)
            summary_frame.index = pd.RangeIndex(start=0, stop=TS.shape[0]+steps, step=1)
            self.dummies.STL['observed'] = TS
            self.dummies.STL['prediction'] = summary_frame['mean']
            self.dummies.STL['prediction_lower'] = summary_frame['pi_lower']
            self.dummies.STL['prediction_upper'] = summary_frame['pi_upper']

            # VIsualization
            if visualize:
                plt.style.use('ggplot')
                _, axes = plt.subplots(4,1, figsize=(13,15))
                axes[0].fill_between(summary_frame.index,
                                     summary_frame['pi_lower'].values,
                                     summary_frame['pi_upper'].values,
                                     color='grey', label='confidence interval')
                axes[0].plot(TS.values, lw=0, marker='o', c='black', label='samples')
                axes[0].plot(summary_frame['mean'], c='red', label='model-forecast')
                axes[0].plot(TS.shape[0]-1+steps, summary_frame['mean'].values[-1], marker='*', markersize=10,  c='red')
                axes[0].axvline(0, ls=':', c='red')
                axes[0].axvline(TS.shape[0]-1, c='red')
                axes[0].axhline(summary_frame['mean'].values[-1], lw=0.5, ls=':', c='gray')
                axes[0].legend()
                axes[1].plot(result.trend, marker='o')
                axes[2].plot(result.seasonal, marker='o')
                axes[3].plot(result.resid, marker='o')
                axes[0].set_title('[Observed]')
                axes[1].set_title('[Trend]')
                axes[2].set_title('[Seasonal]')
                axes[3].set_title('[Resid]')
                plt.tight_layout()
                #plt.show()
        else:
            raise NotImplementedError('The model is not yet prepared.')

        return model.summary()


    #https://www.statsmodels.org/devel/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html#statsmodels.tsa.statespace.sarimax.SARIMAX
    def SARIMAX(self, steps=1, visualize=True,
                exog=None, order=(3, 1, 0), seasonal_order=(3, 1, 0, 5), trend='ct',
                measurement_error=False, time_varying_regression=False,
                mle_regression=True, simple_differencing=False,
                enforce_stationarity=True, enforce_invertibility=True,
                hamilton_representation=False, concentrate_scale=False,
                trend_offset=1, use_exact_diffuse=False, dates=None,
                freq=None, missing='none', validate_specification=True,
                **kwargs):
        self.dummies.SARIMAX = dict()
        
        # Forecast
        TS = self.TS
        model = smt.SARIMAX(TS, exog=exog, order=order,
                            seasonal_order=seasonal_order, trend=trend,
                            measurement_error=measurement_error, time_varying_regression=time_varying_regression,
                            mle_regression=mle_regression, simple_differencing=simple_differencing,
                            enforce_stationarity=enforce_stationarity, enforce_invertibility=enforce_invertibility,
                            hamilton_representation=hamilton_representation, concentrate_scale=concentrate_scale,
                            trend_offset=trend_offset, use_exact_diffuse=use_exact_diffuse, dates=dates,
                            freq=freq, missing=missing, validate_specification=validate_specification,
                            **kwargs).fit()
        self.models['SARIMAX'] = model
        #self.models['SARIMAX'].test_serial_correlation(None)
        #self.models['SARIMAX'].test_heteroskedasticity(None)
        #self.models['SARIMAX'].test_normality(None)
        #self.models['SARIMAX'].arparams
        #self.models['SARIMAX'].maparams
        #self.models['SARIMAX'].seasonalarparams
        #self.models['SARIMAX'].seasonalmaparams
        #self.models['SARIMAX'].get_prediction(start=0, end=330).summary_frame(alpha=0.05)
        #self.models['SARIMAX'].get_prediction(start=0, end=330).conf_int(alpha=0.05)
        #self.models['SARIMAX'].aic
        #self.models['SARIMAX'].bic
        #self.models['SARIMAX'].mse

        _summary_frame = model.get_prediction(start=0, end=TS.shape[0]-1+steps).summary_frame(alpha=0.05)
        summary_frame = _summary_frame.iloc[order[1]+seasonal_order[1]*seasonal_order[3]:]
        self.dummies.SARIMAX['observed'] = TS
        self.dummies.SARIMAX['prediction'] = _summary_frame['mean']
        self.dummies.SARIMAX['prediction_lower'] = _summary_frame['mean_ci_lower']
        self.dummies.SARIMAX['prediction_upper'] = _summary_frame['mean_ci_upper']

        # Visualization
        if visualize:
            plt.style.use('ggplot')
            plt.figure(figsize=(13,5))
            plt.fill_between(summary_frame.index,
                             summary_frame['mean_ci_lower'], 
                             summary_frame['mean_ci_upper'], 
                             color='grey', label='confidence interval')
            plt.plot(TS, lw=0, marker='o', c='black', label='samples')
            plt.plot(summary_frame['mean'], c='red', label='model-forecast')
            plt.plot(TS.shape[0]-1+steps, summary_frame['mean'].values[-1], marker='*', markersize=10,  c='red')
            plt.axvline(0, ls=':', c='red')
            plt.axvline(TS.shape[0]-1, c='red')
            plt.axhline(summary_frame['mean'].values[-1], lw=0.5, c='gray')
            plt.legend()
            #plt.show()

        return model.summary()


    #https://www.statsmodels.org/devel/generated/statsmodels.tsa.exponential_smoothing.ets.ETSModel.html#statsmodels.tsa.exponential_smoothing.ets.ETSModel
    def ETS(self, steps=1, visualize=True,
            error="mul", trend="add", damped_trend=True, seasonal="add", seasonal_periods=5,
            initialization_method="estimated", initial_level=None, initial_trend=None, initial_seasonal=None,
            bounds=None, dates=None, freq=None, missing="none"):
        self.dummies.ETS = dict()
        
        TS = self.TS
        model = smt.ETSModel(TS, error=error, trend=trend, damped_trend=damped_trend, seasonal=seasonal, seasonal_periods=seasonal_periods,
                             initialization_method=initialization_method, initial_level=initial_level, initial_trend=initial_trend, initial_seasonal=initial_seasonal,
                             bounds=bounds, dates=dates, freq=freq, missing=missing).fit(use_boxcox=True)
        self.models['ETS'] = model
        #self.models['ETS'].test_serial_correlation(None)
        #self.models['ETS'].test_heteroskedasticity(None)
        #self.models['ETS'].test_normality(None)
        #self.models['ETS'].states
        #self.models['ETS'].get_prediction(start=0, end=330).summary_frame(alpha=0.05)
        #self.models['ETS'].aic
        #self.models['ETS'].bic
        #self.models['ETS'].mse

        summary_frame = model.get_prediction(start=0, end=TS.shape[0]-1+steps).summary_frame(alpha=0.05)
        self.dummies.ETS['observed'] = TS
        self.dummies.ETS['prediction'] = summary_frame['mean']
        self.dummies.ETS['prediction_lower'] = summary_frame['pi_lower']
        self.dummies.ETS['prediction_upper'] = summary_frame['pi_upper']

        # Visualization
        if visualize:
            plt.style.use('ggplot')
            plt.figure(figsize=(13,5))
            plt.fill_between(summary_frame.index, summary_frame['pi_lower'].values, summary_frame['pi_upper'].values, color='grey', label='confidence interval')
            plt.plot(TS, lw=0, marker='o', c='black', label='samples')
            plt.plot(summary_frame['mean'], c='red', label='model-forecast')
            plt.plot(TS.shape[0]-1+steps, summary_frame['mean'].values[-1], marker='*', markersize=10,  c='red')
            plt.axvline(0, ls=':', c='red')
            plt.axvline(TS.shape[0]-1, c='red')
            plt.axhline(summary_frame['mean'].values[-1], lw=0.5, c='gray')
            plt.legend()
            #plt.show()

        return model.summary()


    #https://www.statsmodels.org/devel/generated/statsmodels.tsa.vector_ar.var_model.VAR.html#statsmodels.tsa.vector_ar.var_model.VAR
    def VAR(self, steps=1, visualize=True,
            exog=None, dates=None, freq=None, missing='none'):
        self.dummies.VAR = dict()

        TS = self._TS.array
        model = smt.VAR(endog=TS, exog=exog, dates=dates, freq=freq, missing=missing).fit()
        
        # Visualization
        if visualize:
            plt.style.use('ggplot')
            plt.figure(figsize=(13,5))
            plt.legend()
            #plt.show()

        self.models['VAR'] = model
        #self.models['VAR'].irf(periods=10).irfs
        #self.models['VAR'].irf(periods=10).plot()
        #self.models['VAR'].irf(periods=10).plot_cum_effects()
        #self.models['VAR'].fevd(periods=10).plot()

        return model.summary()


    #https://www.statsmodels.org/devel/generated/statsmodels.tsa.vector_ar.vecm.VECM.html#statsmodels.tsa.vector_ar.vecm.VECM
    def VECM(self, steps=1, exog=None, exog_coint=None, dates=None,
             freq=None, missing="none", k_ar_diff=1, coint_rank=1,
             deterministic="ci", seasons=4, first_season=0):
        self.dummies.VECM = dict()

        # Forecast
        TS = self._TS.array
        lag_order = select_order(data=TS, maxlags=10, deterministic="ci", seasons=4)
        rank_test = select_coint_rank(endog=TS, det_order=0, k_ar_diff=lag_order.aic, method="trace", signif=0.05)

        model = smt.VECM(endog=TS, exog=exog, exog_coint=exog_coint, dates=dates,
                         freq=freq, missing=missing, k_ar_diff=lag_order.aic, coint_rank=rank_test.rank,
                         deterministic=deterministic, seasons=seasons, first_season=first_season).fit()
        self.models['VECM'] = model
        #self.models['VECM'].test_granger_causality(caused=self.dummies.__init__['select_col'], signif=0.05).signif
        #self.models['VECM'].test_granger_causality(caused=self.dummies.__init__['select_col'], signif=0.05).pvalue
        #self.models['VECM'].test_inst_causality(causing=self.dummies.__init__['select_col']).summary()
        #self.models['VECM'].test_normality().test_statistic
        #self.models['VECM'].test_normality().crit_value
        #self.models['VECM'].test_normality().pvalue
        #self.models['VECM'].test_normality().summary()
        #self.models['VECM'].test_whiteness(nlags=12, adjusted=True).test_statistic
        #self.models['VECM'].test_whiteness(nlags=12, adjusted=True).crit_value
        #self.models['VECM'].test_whiteness(nlags=12, adjusted=True).pvalue
        #self.models['VECM'].test_whiteness(nlags=12, adjusted=True).summary()
        #self.models['VECM'].irf(periods=30)
        #self.models['VECM'].var_rep
        #self.models['VECM'].ma_rep(maxn=2)

        # VIsualization
        if visualize:
            plt.style.use('ggplot')
            plt.figure(figsize=(13,5))
            plt.legend()
            #plt.show()

        return model.summary()



    #https://www.statsmodels.org/devel/generated/statsmodels.tsa.statespace.varmax.VARMAX.html#statsmodels.tsa.statespace.varmax.VARMAX
    def VARMAX(self, steps=1, exog=None, order=(1, 0), trend='c',
               error_cov_type='unstructured', measurement_error=False,
               enforce_stationarity=True, enforce_invertibility=True, trend_offset=1):
        self.dummies.VARMAX = dict()
        
        # Forecast
        TS = self._TS.array
        model = smt.VARMAX(endog=TS, exog=exog, order=order, trend=trend,
                           error_cov_type=error_cov_type, measurement_error=measurement_error,
                           enforce_stationarity=enforce_stationarity, enforce_invertibility=enforce_invertibility,
                           trend_offset=trend_offset).fit()
        self.models['VARMAX'] = model
        #self.models['VARMAX'].impulse_responses(steps=10)

        # Visualization
        if visualize:
            plt.style.use('ggplot')
            plt.figure(figsize=(13,5))
            plt.legend()
            #plt.show()

        return model.summary()
