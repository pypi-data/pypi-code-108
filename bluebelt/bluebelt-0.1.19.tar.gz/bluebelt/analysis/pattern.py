import datetime
import warnings

import pandas as pd

import numpy as np
import scipy.stats as stats

import matplotlib.pyplot as plt

import bluebelt.core.helpers
import bluebelt.core.decorators
import bluebelt.graph.defaults

import bluebelt.styles

import bluebelt.core.index

@bluebelt.core.decorators.class_methods
class Polynomial():
    """
    Find the polynomial of a series and project a bandwidth

    Polynomial(series, shape=(0, 6), validation='p_value', threshold=0.05, confidence=0.8, outlier_sigma=2, adjust=True, **kwargs)
    
    series: pandas.Series
    shape: int or tuple
        when an int is provided the polynomial is provided as n-th degree polynomial
        when a tuple is provided the function will find an optimised polynomial between first and second value of the tuple
        default value: (0, 6)
    validation: string
        validation type for shape tuple
        p_val: test for normal distribution of the residuals
        rsq: check for improvement of the rsq value
        default value: p_val
    threshold: float
        the threshold for normal distribution test or rsq improvement
        default value: 0.05
    confidence: float
        the bound confidence
        default value: 0.8
    outlier_sigma: float
        outliers are datapoints outside the outlier_sigma fraction
        default value: 2
    adjust: boolean
        adjust polynomial for outliers
        default value: True

    """
    def __init__(self, series, shape=(0, 6), validation='rsq', threshold=0.05, confidence=0.8, outlier_sigma=2, adjust=True, **kwargs):
        
        self.series = series
        self.name = series.name or 'series'
        self.shape = shape
        self.validation = validation
        self.threshold = threshold
        self.confidence = confidence
        self.outlier_sigma = outlier_sigma
        self.adjust = adjust

        self.calculate()

    def calculate(self):
        
        # set pattern and residuals
        _poly_hand_granade(self)

        # set outliers
        self.outliers = pd.Series(data=np.where(self.residuals.abs() > self.residuals.std() * self.outlier_sigma, self.series, None), index=self.series.index)
        self.outliers_count = np.count_nonzero(self.outliers)

        # handle adjusted
        self.adjusted = self.series.loc[~self.outliers.notnull()]
        if self.adjust:
            
            self._series = self.series.copy() # backup
            
            # replace outliers with None values so they will be ignored by _poly_hand_granade and reset pattern
            self.series = pd.Series(data=np.where(self.outliers.notnull(), None, self.series).astype(np.float), index=self.series.index)
            _poly_hand_granade(self)

            self.series = self._series.copy() # and reset
            del self._series

        # handle bounds
        _calculate_bounds(self)

        # set final shape
        if hasattr(self, '_shape'):
            self.shape = self._shape
            del self._shape


    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.series.size:1.0f}, shape={self.shape}, validation=\'{self.validation}\', threshold={self.threshold}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust}, outliers={self.outliers_count}, rsq={self.rsq:1.2f}, std={self.std:1.2f}, p_value={self.p_value:1.2f})')
    
    def __str__(self):
        _result = f'input variables\n'
        _result += f'-'*50 + '\n'
        _result += f'  {"series size:":<30}{self.series.size:1.0f}\n'
        _result += f'  {"validation type:":<30}{self.validation}\n'
        _result += f'  {"validation threshold:":<30}{self.threshold:1.4f}\n'
        
        _result += f'\n'
        _result += f'pattern\n'
        _result += f'-'*50 + '\n'
        _result += f'  {"shape:":<30}{self.shape:1.0f}\n'
        _result += f'  {"r squared:":<30}{self.rsq:1.2f}\n'
        

        _result += f'\n'
        _result += f'residuals\n'
        _result += f'-'*50 + '\n'
        _result += f'  {"bounds level:":<30}{self.confidence * 100:1.0f}%\n'
        _result += f'  {"bounds size:":<30}{self.bounds * 2:1.2f}\n'
        _result += f'  {"standard deviation:":<30}{self.std:1.2f}\n'
        _result += f'  {"p-value normal distribution:":<30}{self.p_value:1.4f}\n'
        _result += f'  {"outliers:":<30}{self.outliers_count:1.0f}\n'
        
        return _result

    def plot(self, **kwargs):
        
        return _pattern_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class Periodical():
    
    """
    Find the periodical pattern of a series and project a bandwidth

    Periodical(series, rule='1W', how='mean', resolution=None, confidence=0.8, outlier_sigma=2, adjust=True, **kwargs)
    
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
        self.result, self.residuals, self.statistic, self.p_value, self.rsq = _peri_hand_granade(series=self.series, rule=self.rule, how=self.how, resolution=self.resolution)

        # set outliers
        self.outliers = pd.Series(data=np.where(self.residuals.abs() > self.residuals.std() * self.outlier_sigma, self.series, None), index=self.series.index, name=f'{self.series.name} {_get_nice_polynomial_name(self._shape)} outliers')
        self.outliers_count = np.count_nonzero(self.outliers)

        # handle adjusted
        self.adjusted = self.series.loc[~self.outliers.notnull()]
        if self.adjust:
            # replace outliers with None values so they will be ignored by _peri_hand_granade and reset pattern
            values = pd.Series(data=np.where(self.outliers.notnull(), None, self.series).astype(np.float), index=self.series.index)
            self.result, self.residuals, self.statistic, self.p_value, self.rsq = _peri_hand_granade(series=values, rule=self.rule, how=self.how, resolution=self.resolution)
        
        self.result.rename(f'periodical ({self.rule})', inplace=True)

        # handle bounds
        _calculate_bounds(self)

        # 

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.series.size:1.0f}, rule={self.rule}, how={self.how}, resolution={self.resolution}, confidence={self.confidence}, outlier_sigma={self.outlier_sigma}, adjust={self.adjust}, outliers={self.outliers_count})')
    
    def plot(self, **kwargs):
        return _pattern_plot(self, **kwargs)


# helper functions
def _poly_hand_granade(_obj):

    if isinstance(_obj.series.index, (bluebelt.core.index.DatetimeMultiIndex, bluebelt.core.index.IsoDatetimeMultiIndex, bluebelt.core.index.DayOfYearMultiIndex)):
        index = np.array([d.timestamp() for d in _obj.series.index.to_datetimeindex()], dtype='int')
        index = index - index.min()
        index = index / np.gcd.reduce(index)

        # drop nan values
        _index = np.array([d.timestamp() for d in _obj.series.index.to_datetimeindex().dropna()], dtype='int')
        _index = _index - _index.min()
        _index = _index / np.gcd.reduce(_index)

    elif isinstance(_obj.series.index, pd.DatetimeIndex) and _obj.series.index.freqstr == "D":
        index = np.array([d.timestamp() for d in _obj.series.index], dtype='int')
        index = index - index.min()
        index = index / np.gcd.reduce(index)

        # drop nan values
        _index = np.array([d.timestamp() for d in _obj.series.dropna().index], dtype='int')
        _index = _index - _index.min()
        _index = _index / np.gcd.reduce(_index)

    else:
        index = np.arange(0, _obj.series.size)
        _index = np.arange(0, _obj.series.dropna().size)
        

    # get the values
    _values = _obj.series.dropna().values

    if isinstance(_obj.shape, int):
        polyfit = np.polynomial.polynomial.polyfit(_index, _values, _obj.shape)
        _obj.result = pd.Series(index=_obj.series.index, data=np.polynomial.polynomial.polyval(index, polyfit), name=f'{_obj.name} {_get_nice_polynomial_name(_obj.shape)}')
        _obj.residuals = (_obj.series - _obj.result).rename(f'{_obj.name} {_get_nice_polynomial_name(_obj.shape)} residuals')
                    
        _obj.statistic, _obj.p_value = stats.normaltest(_obj.residuals.dropna().values)
        np_err = np.seterr(divide='ignore', invalid='ignore') # ignore possible divide by zero
        _obj.rsq = np.corrcoef(_obj.series.dropna().values, _obj.result[~_obj.series.isna()].values)[1,0]**2
        np.seterr(**np_err) # go back to previous settings
        _obj.std = _obj.residuals.std()
        
    elif isinstance(_obj.shape, tuple):
        
        _results = {}
        _validation = {}

        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            for shape in range(_obj.shape[0], _obj.shape[1]+1):
                try:
                    polyfit = np.polynomial.polynomial.polyfit(_index, _values, shape)
                    result = pd.Series(index=_obj.series.index, data=np.polynomial.polynomial.polyval(index, polyfit), name=f'{_obj.name} {_get_nice_polynomial_name(shape)}')
                    residuals = (_obj.series - result).rename(f'{_obj.name} {_get_nice_polynomial_name(shape)} residuals')
                    
                    statistic, p_value = stats.normaltest(residuals.dropna().values)
                    np_err = np.seterr(divide='ignore', invalid='ignore') # ignore possible divide by zero
                    rsq = np.corrcoef(_obj.series.dropna().values, result[~_obj.series.isna()].values)[1,0]**2
                    np.seterr(**np_err) # go back to previous settings
                    std = residuals.std()

                    _results[shape] = {
                        'result': result,
                        'residuals': residuals,
                        'statistic': statistic,
                    }
                    _validation[shape] = {
                        'p_value': p_value,
                        'rsq': rsq,
                        'std': std,
                    }
                    

                except np.polynomial.polynomial.pu.RankWarning:
                    print(f'RankWarning at {_get_nice_polynomial_name(shape)}')
                    break
        
        if _obj.validation == 'p_value':
            validation = pd.DataFrame.from_dict(_validation).loc[_obj.validation]
            
            # if any p_value >= threshold then we have a winner
            if (validation >= _obj.threshold).any():
                shape = validation.idxmax()
            else:
                shape = 0

        elif _obj.validation == 'std':

            # we want a small std of the residuals
            validation = pd.DataFrame.from_dict(_validation).loc[_obj.validation]

            # are there any relevant improvements?
            if (validation.diff().abs()/validation.shift() >= _obj.threshold).any():
                # find the relevant improvements
                relevant = validation.iloc[validation.diff().idxmin():]
                
                # does it get any better than this?
                improvements = (relevant.diff()/relevant.shift(1)).abs() >= _obj.threshold
                improvements.at[validation.diff().idxmin()] = True # because it must be
                
                # where does it stop getting better?
                first_fail = improvements.where(improvements == False).first_valid_index() or improvements.index.max()+1
                
                # so what is the shape?
                shape = improvements[improvements.index<first_fail].index.max()
            else:
                shape = validation.index[0]

        else: # the default
            _obj.validation = 'rsq'
            
            # we want a big rsq value
            validation = pd.DataFrame.from_dict(_validation).loc[_obj.validation]

            # are there any relevant improvements?
            if (validation.diff().abs()/validation.shift() >= _obj.threshold).any():
                # find the relevant improvements
                relevant = validation.iloc[validation.diff().idxmax():]
                
                # does it get any better than this?
                improvements = (relevant.diff()/relevant.shift(1)).abs() >= _obj.threshold
                improvements.at[validation.diff().idxmax()] = True # because it must be
                
                # where does it stop getting better?
                first_fail = improvements.where(improvements == False).first_valid_index() or improvements.index.max()+1
                
                # so what is the shape?
                shape = improvements[improvements.index<first_fail].index.max()
            else:
                shape = validation.index[0]


        _obj.result = _results.get(shape).get('result')
        _obj.residuals = _results.get(shape).get('residuals')
        _obj._shape = shape
        _obj.statistic = _results.get(shape).get('statistic')
        _obj.p_value = _validation.get(shape).get('p_value')
        _obj.rsq = _validation.get(shape).get('rsq')
        _obj.std = _validation.get(shape).get('std')
        
    else:
        _obj.result = None
        _obj.residuals = None

    return

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
    _obj.upper = _obj.result + _obj.residuals.std() * _obj.sigma_level
    _obj.lower = _obj.result - _obj.residuals.std() * _obj.sigma_level
    _obj.bounds = _obj.residuals.std() * _obj.sigma_level

    # set out of bounds values
    _obj.out_of_bounds = _obj.series[((_obj.series > _obj.upper) | (_obj.series < _obj.lower)) & (_obj.outliers.isnull())]
    _obj.within_bounds = _obj.series[(_obj.series <= _obj.upper) & (_obj.series >= _obj.lower)]
    

    return _obj

def _pattern_plot(_obj, **kwargs):
        
    style = kwargs.pop('style', bluebelt.styles.paper)
    path = kwargs.pop('path', None)

    bounds = kwargs.pop('bounds', True)
    residuals = kwargs.pop('residuals', False)
    legend = kwargs.pop('legend', True)
    
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    # prepare figure
    fig = plt.figure(constrained_layout=False, **kwargs)
    if residuals:
        gridspec = fig.add_gridspec(nrows=2, ncols=1, height_ratios=[5,3], wspace=0, hspace=0)
        ax2 = fig.add_subplot(gridspec[1, 0], zorder=40)

        # residuals histogram
        bluebelt.graph.defaults.hist(_obj.residuals.values, ax=ax2)
        ax2.set_yticks([])

        # get current limits
        xlims = ax2.get_xlim()
        ylims = ax2.get_ylim()
        
        # fit a normal distribution to the data
        norm_mu, norm_std = stats.norm.fit(_obj.residuals.dropna())
        pdf_x = np.linspace(xlims[0], xlims[1], 100)
        bluebelt.graph.defaults.dotted_line(pdf_x, stats.norm.pdf(pdf_x, norm_mu, norm_std), ax=ax2)
        # ax2.plot(pdf_x, stats.norm.pdf(pdf_x, norm_mu, norm_std), **style.patterns.normal_plot)

        # histogram x label
        ax2.set_xlabel('residuals distribution')
                
        ax2.set_ylim(ylims[0], ylims[1]*1.5)
        ax2.spines['left'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        ax2.text(0.02, 0.7, f'D’Agostino-Pearson\nstatistic: {_obj.statistic:1.2f}\np: {_obj.p_value:1.2f}', transform=ax2.transAxes, **style.patterns.statistics)
    else:
        gridspec = fig.add_gridspec(nrows=1, ncols=1)
        
    ax1 = fig.add_subplot(gridspec[0, 0], zorder=50)
    
    # pattern
    bluebelt.graph.defaults.line(_obj.result.index, _obj.result.values, ax=ax1, zorder=95, label='pattern')
    
    if bounds:
        # observations
        bluebelt.graph.defaults.observations(_obj.within_bounds.index, _obj.within_bounds.values, ax=ax1, zorder=99, label='observations')

        # bounds
        bluebelt.graph.defaults.fill_between(_obj.series.index, _obj.lower.values, _obj.upper.values, ax=ax1, zorder=90, label=f'{(_obj.confidence * 100):1.0f}% bounds')
        bluebelt.graph.defaults.dotted_line(_obj.series.index, _obj.lower.values, ax=ax1, zorder=92, label=None)
        bluebelt.graph.defaults.dotted_line(_obj.series.index, _obj.upper.values, ax=ax1, zorder=92, label=None)
        
        # out of bounds
        bluebelt.graph.defaults.out_of_bounds(_obj.out_of_bounds.index, _obj.out_of_bounds.values, ax=ax1, zorder=85, label='out of bounds')
    else:
        # observations
        bluebelt.graph.defaults.observations(_obj.within_bounds.index, _obj.within_bounds.values, ax=ax1, zorder=99, label='observations')

        # out of bounds
        bluebelt.graph.defaults.observations(_obj.out_of_bounds.index, _obj.out_of_bounds.values, ax=ax1, zorder=85, label='out of bounds')

    # outliers
    bluebelt.graph.defaults.outliers(_obj.outliers.index, _obj.outliers.values, ax=ax1, zorder=80, label='outliers')
        
    # labels
    ax1.set_title(f'{_obj.result.name}', **style.patterns.title)
    ax1.set_ylabel('value')

    # xticks
    if isinstance(_obj.series.index, pd.MultiIndex):
        bluebelt.graph.helpers._get_multiindex_labels(ax1, _obj.series, style)
        fig.subplots_adjust(bottom=.1*_obj.series.index.nlevels)
    elif isinstance(_obj.series.index, pd.DatetimeIndex):
        bluebelt.graph.helpers._axisformat(ax1, _obj.series)

    ax1.set_xlim(xlim)
    ax1.set_ylim(ylim)

    # legend
    if legend:
        ax1.legend(loc='best')
    
    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig