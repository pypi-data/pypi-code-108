import copy
import math
import pandas as pd
import numpy as np


import matplotlib.pyplot as plt
import seaborn as sns

import bluebelt.core.decorators
import bluebelt.core.helpers

import bluebelt.styles.paper

@bluebelt.core.decorators.class_methods
class MAPE():
    """
    Return the mean absolute percentage error.
        arguments
        frame: pandas.Series or pandas.DataFrame
        forecast: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the forecast columns name                    
            if frame is a pandas.Series this can be a pandas.Series with forecast data; frame will be treated as actuals data
            default value None
        actuals: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the actuals columns name                    
            if frame is a pandas.Series this can be a pandas.Series with actuals data; frame will be treated as forecast data
            default value None
        if frame is a pandas.Series only one of forecast and actuals must be provided
    """
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):
        
        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.zero = kwargs.get('zero', 'skip')
        self.calculate()

    def calculate(self):

        self.forecast, self.actuals = _get_data(self)

        # handle zeros
        if self.zero == 'skip':
            self.forecast = self.forecast[self.actuals!=0]
            self.actuals = self.actuals[self.actuals!=0]
        elif isinstance(self.zero, (int, float)):
            self.actuals.loc[self.actuals==0] = self.zero
            
        if self.forecast is not None and self.actuals is not None:
            self.result = (np.abs((self.actuals - self.forecast)/self.actuals).sum()) / len(self.forecast)
            self.values = np.abs((self.actuals - self.forecast)/self.actuals)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f}, zero=\'{self.zero}\')')
    
    def plot(self, **kwargs):
        return _forecast_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class WMAPE():
    """
    Return the weighted mean absolute percentage error.
        arguments
        frame: pandas.Series or pandas.DataFrame
        forecast: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the forecast columns name                    
            if frame is a pandas.Series this can be a pandas.Series with forecast data; frame will be treated as actuals data
            default value None
        actuals: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the actuals columns name                    
            if frame is a pandas.Series this can be a pandas.Series with actuals data; frame will be treated as forecast data
            default value None
        if frame is a pandas.Series only one of forecast and actuals must be provided
    """
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):
        
        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.calculate()

    def calculate(self):

        self.forecast, self.actuals = _get_data(self)
            
        if self.forecast is not None and self.actuals is not None:
            self.result = (np.abs(self.actuals - self.forecast).sum() / np.abs(self.actuals).sum())
            self.values = np.abs((self.actuals - self.forecast)/self.actuals)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f})')
    
    def plot(self, **kwargs):
        return _forecast_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class SMAPE():
    """
    Return the symmetric mean absolute percentage error.
        arguments
        frame: pandas.Series or pandas.DataFrame
        forecast: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the forecast columns name                    
            if frame is a pandas.Series this can be a pandas.Series with forecast data; frame will be treated as actuals data
            default value None
        actuals: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the actuals columns name                    
            if frame is a pandas.Series this can be a pandas.Series with actuals data; frame will be treated as forecast data
            default value None
        if frame is a pandas.Series only one of forecast and actuals must be provided
    """
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):
        
        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.zero = kwargs.get('zero', 'skip')
        self.calculate()

    def calculate(self):

        self.forecast, self.actuals = _get_data(self)

        # handle zeros
        if self.zero == 'skip':
            self.forecast = self.forecast.loc[~((self.forecast==0) & (self.actuals==0))]
            self.actuals = self.actuals.loc[~((self.forecast==0) & (self.actuals==0))]
        elif isinstance(self.zero, (int, float)):
            # forecast is accurate
            self.forecast.loc[((self.forecast==0) & (self.actuals==0))] = 1
            self.actuals.loc[((self.forecast==0) & (self.actuals==0))] = 1
            
        if self.forecast is not None and self.actuals is not None:
            self.result = (np.abs(self.actuals - self.forecast) / ((np.abs(self.actuals) + np.abs(self.forecast)) / 2) ).sum() / len(self.forecast)
            self.values = np.abs(self.actuals - self.forecast) / ((np.abs(self.actuals) + np.abs(self.forecast)) / 2)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f}, zero=\'{self.zero}\')')
    
    def plot(self, **kwargs):
        return _forecast_plot(self, **kwargs)

@bluebelt.core.decorators.class_methods
class MDA():
    """
    Return the mean mean directional accuracy.
        arguments
        frame: pandas.Series or pandas.DataFrame
        forecast: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the forecast columns name                    
            if frame is a pandas.Series this can be a pandas.Series with forecast data; frame will be treated as actuals data
            default value None
        actuals: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the actuals columns name                    
            if frame is a pandas.Series this can be a pandas.Series with actuals data; frame will be treated as forecast data
            default value None
        if frame is a pandas.Series only one of forecast and actuals must be provided
    """
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):
        
        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.calculate()

    def calculate(self):

        self.forecast, self.actuals = _get_data(self)
        
        if self.forecast is not None and self.actuals is not None:
            self.result = (((self.forecast < self.forecast.shift(-1)).iloc[:-1] == (self.actuals < self.actuals.shift(-1)).iloc[:-1]) * 1).sum() / (len(self.forecast) - 1)
            self.values = (((self.forecast < self.forecast.shift(-1)).iloc[:-1] == (self.actuals < self.actuals.shift(-1)).iloc[:-1]) * 1)
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f})')

@bluebelt.core.decorators.class_methods
class MPE():
    """
    Return the mean percentage error.
        arguments
        frame: pandas.Series or pandas.DataFrame
        forecast: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the forecast columns name                    
            if frame is a pandas.Series this can be a pandas.Series with forecast data; frame will be treated as actuals data
            default value None
        actuals: pandas.Series or str
            if frame is a pandas.DataFrame this must be a string with the actuals columns name                    
            if frame is a pandas.Series this can be a pandas.Series with actuals data; frame will be treated as forecast data
            default value None
        if frame is a pandas.Series only one of forecast and actuals must be provided
    """
    
    def __init__(self, frame, forecast=None, actuals=None, **kwargs):
        
        self.frame = frame
        self.forecast = forecast
        self.actuals = actuals
        self.zero = kwargs.get('zero', 'skip')
        self.calculate()

    def calculate(self):

        self.forecast, self.actuals = _get_data(self)
        
        # handle zeros
        if self.zero == 'skip':
            self.forecast = self.forecast.loc[self.actuals!=0]
            self.actuals = self.actuals.loc[self.actuals!=0]
        elif isinstance(self.zero, (int, float)):
            self.actuals.loc[self.actuals==0] = _obj.zero

        if self.forecast is not None and self.actuals is not None:
            self.result = ((self.actuals - self.forecast)/self.actuals).sum() / len(self.forecast)
            self.values = (self.actuals - self.forecast)/self.actuals
        else:
            self.result = None
            self.values = None

    def __repr__(self):
        return (f'{self.__class__.__name__}(n={self.frame.shape[0]:1.0f}, result={self.result:1.4f}, zero=\'{self.zero}\')')
    
    def plot(self, **kwargs):
        return _forecast_plot(self, **kwargs)

def _get_data(_obj, **kwargs):
    
    # deepcopy object to prevent a mess
    _obj = copy.deepcopy(_obj)

    if isinstance(_obj.frame, pd.Series):
        if isinstance(_obj.forecast, pd.Series):
            forecast = _obj.forecast
            actuals = _obj.frame
        elif isinstance(_obj.actuals, pd.Series):
            forecast = _obj.frame
            actuals = _obj.actuals
        else:
            raise ValueError("Please provide forecast data or actuals data. One pandas Series is not enough to calculate forecast accuracy.")
    elif isinstance(_obj.frame, pd.DataFrame):
        if isinstance(_obj.forecast, str):
            forecast = _obj.frame[_obj.forecast]
        else:
            forecast = _obj.frame.iloc[:,0]

        if isinstance(_obj.actuals, str):
            actuals = _obj.frame[_obj.actuals]
        else:
            actuals = _obj.frame.iloc[:,1]        

    return forecast, actuals

def _forecast_plot(plot_obj, **kwargs):

    style = kwargs.pop('style', bluebelt.styles.paper)
    path = kwargs.pop('path', None)
    bins = kwargs.pop('bins', 20)
    title = kwargs.pop('title', f'{plot_obj.__class__.__name__}')
    values = plot_obj.values.replace([np.inf, -np.inf], np.nan)
    
    xlim = kwargs.pop('xlim', (None, None))
    #ylim = kwargs.pop('ylim', (None, None))
    
    fig, axes = plt.subplots(nrows=1, ncols=1, gridspec_kw={'wspace': 0, 'hspace': 0}, **kwargs)
    
    # plot
    axes.hist(values, bins=bins, **style.forecast.histogram)

    # set xlim
    xlim_lower, xlim_upper = xlim
    xlim_lower = xlim_lower or math.floor(values.min())
    xlim_upper = xlim_upper or math.ceil(values.max())
    xlim = (xlim_lower, xlim_upper)
    axes.set_xlim(xlim)
    
    # transform xticklabels to percentage
    axes.set_xticks(axes.get_xticks())
    axes.set_xticklabels([f'{x:1.0%}' for x in axes.get_xticks()])

    # remove yticks
    axes.set_yticks([])

    # title
    axes.set_title(title, **style.forecast.title)
    
    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig