import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
import scipy.stats as stats

import warnings

import matplotlib.pyplot as plt

import bluebelt.core.helpers
import bluebelt.core.decorators

import bluebelt.styles

@bluebelt.core.decorators.class_methods
class Polynomial():

    def __init__(self, series, shape=(0, 6), validation='p_value', threshold=0.05, confidence=0.8, outlier_sigma=2, adjust=True, **kwargs):
        
        self.series = series
        self.shape = shape
        self.validation = validation
        self.threshold = threshold
        self.confidence = confidence
        self.outlier_sigma = outlier_sigma
        self.adjust = adjust

        self.calculate()

    def calculate(self):
        
        # set pattern and residuals
        self.pattern, self.residuals, self.statistic, self.p_value, self.rsq = _poly_hand_granade(series=self.series, shape=self.shape, validation=self.validation, threshold=self.threshold)

        # set outliers
        self.outliers = pd.Series(data=np.where(self.residuals.abs() > self.residuals.std() * self.outlier_sigma, self.series, None), index=self.series.index)
        self.outliers_count = np.count_nonzero(self.outliers)

        # handle adjusted
        self.adjusted = self.series.loc[~self.outliers.notnull()]
        if self.adjust:
            # replace outliers with None values so they will be ignored by _poly_hand_granade and reset pattern
            values = pd.Series(data=np.where(self.outliers.notnull(), None, self.series).astype(np.float), index=self.series.index)
            self.pattern, self.residuals, self.statistic, self.p_value, self.rsq = _poly_hand_granade(series=values, shape=self.shape, validation=self.validation, threshold=self.threshold)
        
        # handle bounds
        _calculate_bounds(self)

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.series.size:1.0f}, shape={self.shape}, validation={self.validation}, threshold={self.threshold}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust}, outliers={self.outliers_count})')
    
    def plot(self, **kwargs):
        
        return _pattern_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class Periodical():
    
    """
    Find the periodical pattern of a series and project a bandwidth
    series: pandas.Series
    rule: period representation used for resampling the series
        default value: "1W"
    how: define how the period must be evaluated
        options are "mean", "min", "max" and "std"
        default value: "mean"
    resolution: define the resolution of the pattern
        the pattern is rounded to fit the resolution
        default value: None
    confidence: float
        the bandwidth confidence
        default value: 0.8
    outlier_sigma: float
        outliers are datapoints outside the outlier_sigma fraction
        default value: 2
    
    """

    def __init__(self, series, rule='1W', how='mean', resolution=None, confidence=0.8, outlier_sigma=2, adjust=True, **kwargs):
        
        self.series = series
        self.rule = rule
        self.how = how
        self.resolution = resolution
        self.confidence = confidence
        self.outlier_sigma = outlier_sigma
        self.adjust = adjust
        
        self.calculate()

    def calculate(self):
        
        # set pattern and residuals        
        self.pattern, self.residuals, self.statistic, self.p_value, self.rsq = _peri_hand_granade(series=self.series, rule=self.rule, how=self.how, resolution=self.resolution)

        # set outliers
        self.outliers = pd.Series(data=np.where(self.residuals.abs() > self.residuals.std() * self.outlier_sigma, self.series, None), index=self.series.index)
        self.outliers_count = np.count_nonzero(self.outliers)

        # handle adjusted
        self.adjusted = self.series.loc[~self.outliers.notnull()]
        if self.adjust:
            # replace outliers with None values so they will be ignored by _peri_hand_granade and reset pattern
            values = pd.Series(data=np.where(self.outliers.notnull(), None, self.series).astype(np.float), index=self.series.index)
            self.pattern, self.residuals, self.statistic, self.p_value, self.rsq = _peri_hand_granade(series=values, rule=self.rule, how=self.how, resolution=self.resolution)
        
        self.pattern.rename(f'periodical ({self.rule})', inplace=True)

        # handle bounds
        _calculate_bounds(self)

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.series.size:1.0f}, rule={self.rule}, how={self.how}, resolution={self.resolution}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust}, outliers={self.outliers_count})')
    
    def plot(self, **kwargs):
        return _pattern_plot(self, **kwargs)

# helper functions
def _poly_hand_granade(series, shape=(0, 6), validation='p_value', threshold=0.05, **kwargs):

    """
    Find the polynomial of a series.
    series = the pandas Series
    shape: int or tuple
        when an int is provided the polynomial is provided as n-th degree polynomial
        when a tuple is provided the function will find an optimised polynomial between first and second value of the tuple
    validation: only for tuple shape
        p_value: test for normal distribution of the residuals
        rsq: check for improvement of the rsq value
    threshold: the threshold for normal distribution test or rsq improvement
    """

    # get the index
    index = series.index.astype(int)-series.index.astype(int).min()
    index = index / np.gcd.reduce(index)

    # drop nan values
    _index = series.dropna().index.astype(int)-series.index.astype(int).min()
    _index = _index / np.gcd.reduce(_index)

    # get the values
    values = series.dropna().values

    # set first rsq
    _rsq = 0


    if isinstance(shape, int):
        pattern = pd.Series(index=series.index, data=np.polynomial.polynomial.polyval(index, np.polynomial.polynomial.polyfit(_index, values, shape)), name=f'{_get_nice_polynomial_name(shape)}')
        residuals = pd.Series(index=series.index, data=[a - b for a, b in zip(series.values, pattern)])
        
        statistic, p_value = stats.normaltest(residuals.dropna().values)
        rsq = np.corrcoef(series.values, pattern.values)[1,0]**2

    elif isinstance(shape, tuple):

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            for shape in range(shape[0], shape[1]+1):
                try:
                    pattern = pd.Series(index=series.index, data=np.polynomial.polynomial.polyval(index, np.polynomial.polynomial.polyfit(_index, values, shape)), name=f'{_get_nice_polynomial_name(shape)}')
                    residuals = pd.Series(index=series.index, data=[a - b for a, b in zip(series.values, pattern)])
                    
                    np_err = np.seterr(divide='ignore', invalid='ignore') # ignore possible divide by zero
                    rsq = np.corrcoef(series.values, pattern.values)[1,0]**2
                    np.seterr(**np_err) # go back to previous settings
                    
                    statistic, p_value = stats.normaltest(residuals.dropna().values)

                    if validation=='p_value' and p_value >= threshold:
                        break
                    elif validation=='rsq' and (rsq - _rsq) / rsq < threshold:
                        pattern = pd.Series(index=series.index, data=poly.polyval(index, poly.polyfit(_index, values, shape-1)), name=f'{_get_nice_polynomial_name(shape-1)}')    
                        residuals = pd.Series(index=series.index, data=[a - b for a, b in zip(series.values, pattern)])
                        
                        # reset rsq
                        rsq = _rsq
                        break
                    
                    # set previous rsq to current rsq
                    _rsq = rsq

                except poly.pu.RankWarning:
                    print(f'RankWarning at {_get_nice_polynomial_name(shape)}')
                    break
    else:
        pattern = None
        residuals = None

    return pattern, residuals, statistic, p_value, rsq

def _peri_hand_granade(series, rule, how, resolution, **kwargs):

    # set pattern and residuals
    if how=='mean':
        pattern = series.resample(rule=rule).mean()
    elif how=='min':
        pattern = series.resample(rule=rule).min()
    elif how=='max':
        pattern = series.resample(rule=rule).max()
    elif how=='std':
        pattern = series.resample(rule=rule).std()
    else:
        pattern = series.resample(rule=rule).sum()
    
    # reindex pattern
    if any([period for period in ['M', 'A', 'Q', 'BM', 'BA', 'BQ', 'W'] if (period == "".join(char for char in rule if not char.isnumeric()))]):
        pattern = pattern.reindex_like(series, method = 'bfill')
    else:
        pattern = pattern.reindex_like(series, method = 'ffill')

    if resolution:
        # adjust for resolution
        pattern = pattern.divide(resolution).round(0).multiply(resolution)
    
    residuals = series - pattern

    statistic, p_value = stats.normaltest(residuals.dropna().values)
    rsq = np.corrcoef(series.values, pattern.values)[1,0]**2

    return pattern, residuals, statistic, p_value, rsq

def _get_nice_polynomial_name(shape):
    if shape==0:
        return 'linear'
    if shape==1:
        return str(shape)+'st degree polynomial'
    elif shape==2:
        return str(shape)+'nd degree polynomial'
    elif shape==3:
        return str(shape)+'rd degree polynomial'
    else:
        return str(shape)+'th degree polynomial'

def _calculate_bounds(_obj):
        
    _obj.sigma_level = stats.norm.ppf(1-(1-_obj.confidence)/2)

    # set bounds
    _obj.upper = _obj.pattern + _obj.residuals.std() * _obj.sigma_level
    _obj.lower = _obj.pattern - _obj.residuals.std() * _obj.sigma_level
    _obj.bounds = _obj.residuals.std() * _obj.sigma_level

    # set out of bounds values
    _obj.out_of_bounds = _obj.series[((_obj.series > _obj.upper) | (_obj.series < _obj.lower)) & (_obj.outliers.isnull())]

    return _obj

def _pattern_plot(_obj, **kwargs):
        
    style = kwargs.pop('style', bluebelt.styles.paper)
    path = kwargs.pop('path', None)

    bounds = kwargs.pop('bounds', True)
    residuals = kwargs.pop('residuals', True)
    
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    # prepare figure
    fig = plt.figure(constrained_layout=False, **kwargs)
    if residuals:
        gridspec = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[5,3], wspace=0, hspace=0)
        ax2 = fig.add_subplot(gridspec[1, 0], zorder=40)
    else:
        gridspec = fig.add_gridspec(nrows=1, ncols=1)
        
    ax1 = fig.add_subplot(gridspec[0, 0], zorder=50)
    
    # observations
    ax1.plot(_obj.series, **style.patterns.observations)

    # pattern
    ax1.plot(_obj.pattern, **style.patterns.pattern)
    
    # outliers
    ax1.plot(_obj.outliers, **style.patterns.outlier_background)
    ax1.plot(_obj.outliers, **style.patterns.outlier)

    # bounds
    if bounds:
        ax1.fill_between(_obj.series.index, _obj.lower, _obj.upper, label=f'{(_obj.confidence * 100):1.0f}% bounds', **style.patterns.bandwidth_fill_between)
        ax1.plot(_obj.lower, **style.patterns.lower)
        ax1.plot(_obj.upper, **style.patterns.upper)
    
        # out of bounds
        ax1.plot(_obj.out_of_bounds, **style.patterns.out_of_bounds)

        ax1.legend(loc='best')
        
    # labels
    ax1.set_title(f'{_obj.series.name} {_obj.pattern.name}', **style.patterns.title)
    ax1.set_ylabel('value')

    # set x axis locator
    bluebelt.core.helpers._axisformat(ax1, _obj.series)

    if residuals:
        # residuals histogram
        ax2.hist(_obj.residuals, **style.patterns.histogram)
        ax2.set_yticks([])

        # get current limits
        xlims = ax2.get_xlim()
        ylims = ax2.get_ylim()
        
        # fit a normal distribution to the data
        norm_mu, norm_std = stats.norm.fit(_obj.residuals.dropna())
        pdf_x = np.linspace(xlims[0], xlims[1], 100)
        ax2.plot(pdf_x, stats.norm.pdf(pdf_x, norm_mu, norm_std), **style.patterns.normal_plot)

        # histogram x label
        ax2.set_xlabel('residuals distribution')
                
        ax2.set_ylim(ylims[0], ylims[1]*1.5)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        ax2.text(0.02, 0.7, f'D’Agostino-Pearson\nstatistic: {_obj.statistic:1.2f}\np: {_obj.p_value:1.2f}', transform=ax2.transAxes, **style.patterns.statistics)

    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)
    
    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig