import numpy as np
import pandas as pd

import scipy.stats

import matplotlib.pyplot as plt

import bluebelt.statistics.constants as constants

import bluebelt.core.decorators
import bluebelt.core.helpers

import bluebelt.styles

@bluebelt.core.decorators.class_methods
class RollingStd():
    
    """
    Show the rolling standard deviation of a pandas series
    series: pandas.Series
    window: int
        the window size
        default value: 7
    center: boolean
        center the labels
        default value: True
    accepts all arguments for pd.Series.Rolling
    """

    def __init__(self, series, window=7, center=True, **kwargs):
        
        self.series = series
        self.window = window
        self.center = center
        self.win_type = kwargs.get('win_type', None)
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        self.rolling = self.series.dropna().rename(f'{self.series.name} rolling std').rolling(window=self.window, center=self.center, **kwargs).std()
        

    def plot(self, **kwargs):
        
        title = kwargs.pop('title', f'{self.series.name} rolling standard deviation')
        style = kwargs.pop('style', bluebelt.styles.paper)
        
        path = kwargs.pop('path', None)        
        
        # prepare figure
        fig, ax = plt.subplots(**kwargs)
        
        # area plot
        ax.stackplot(self.rolling.index, self.rolling, **style.graphs.area.stackplot)
        ax.plot(self.rolling.index, self.rolling, **style.graphs.area.plot)
        
        # labels
        ax.set_title(title, **style.graphs.area.title)
        
        # set x axis locator
        bluebelt.graph.helpers._axisformat(ax, self.series)
        ax.set_ylim(0,)

        if path:
            plt.savefig(path)
            plt.close()
        else:
            plt.close()
            return fig

@bluebelt.core.decorators.class_methods
class StdWithin():
    """
    Calculate the standard deviation within subgroups.
        arguments
        frame: pandas.DataFrame or pandas.Series
        columns: list
            a list of column names
            if not provided all columns will be treated as subgroups
            if frame is a Pandas Series only the first column will be used
            default value: None
        how: str
            the method of estimating std_within
            options when subgroup size == 1 (default when frame is a Pandas Series):
            - 'amr' or 'average_moving_range'
                optional argument: observations=2
            - 'mmr' or 'median_moving_range'
                optional argument: observations=2
            - 'mssd' or 'sqrt_of_mssd'
            default value: 'amr'

            options when subgroup size > 1:
            - 'pooled_std'
            - 'r_bar'
            - 's_bar'
            default value: 'pooled_std'

        observations: int
            used for average moving range and median moving range estimation
            default value: 2
    """

    def __init__(self, frame, axis=0, columns=None, how=None, observations=2, **kwargs):

        if isinstance(frame, pd.DataFrame) and isinstance(columns, (str, list)):
            frame = frame[columns]

        if isinstance(frame, pd.DataFrame) and axis == 0:
            self.data = frame.values
        elif isinstance(frame, pd.DataFrame):
            self.data = frame.T.values
        elif isinstance(frame, pd.Series):
            self.data = frame.values

        self.frame = frame
        self.columns = columns
        self.axis = axis
        self.how = how
        self.observations = observations
        self.nrows = self.data.shape[0]
        self.ncols = 1 if self.data.ndim == 1 else self.data.shape[1]
        self.calculate(**kwargs)

    def calculate(self, **kwargs):
        # choose how depending on subgroup size
        if self.ncols == 1:
            if self.how in ['mssd', 'sqrt_of_mssd']:
                self.how = 'mssd'
                self.std = _sqrt_of_mssd(self, **kwargs)
            elif self.how in ['mmr', 'median_moving_range']:
                self.how = 'mmr'
                self.std = _median_moving_range(self, **kwargs)
            else:
                self.how = 'amr'
                self.std = _average_moving_range(self, **kwargs)
        
        else:
            if self.how=='r_bar':
                self.std = _r_bar(self, **kwargs)
            elif self.how == 's_bar':
                self.std = _s_bar(self, **kwargs)
            else:
                self.how = 'pooled std'
                self.std = _pooled_std(self, **kwargs)

    def __str__(self):
        return ""
    
    def __repr__(self):
        return (f'{self.__class__.__name__}(nrows={self.nrows}, ncols={self.ncols}, how={self.how}, axis={self.axis}, std={self.std:1.4f})')
    

def std_within(frame, columns=None, axis=0, how=None, observations=2, **kwargs):
    bluebelt.statistics.std.StdWithin(frame, columns=columns, axis=axis, how=how, observations=observations, **kwargs)  

# standard deviation within subgroups with subgroup size == 1
def _average_moving_range(std_obj, **kwargs):
    """
    Calculate the average moving range
    """
        
    periods = std_obj.observations - 1
    if std_obj.observations >= std_obj.nrows:
        raise ValueError(f'The number of observations ({std_obj.observations}) must be lower then the length of the data({std_obj.nrows})')

    return pd.Series(std_obj.data).diff(periods=periods).apply(abs)[periods:].dropna().mean() / constants.d2(std_obj.observations)

def _median_moving_range(std_obj, **kwargs):
    """
    Calculate the median moving range
    """
    
    periods = std_obj.observations - 1
    if std_obj.observations >= std_obj.nrows:
        raise ValueError(f'The number of observations ({std_obj.observations}) must be lower then the length of the series({frame.shape[0]})')

    return pd.Series(std_obj.data).diff(periods=periods).apply(abs)[periods:].dropna().median() / constants.d2(std_obj.observations)

def _sqrt_of_mssd(std_obj, **kwargs):
    """
    Calculate the square root of half of the mean of the squared successive differences
    """
    
    return (0.5 * sum(pd.Series(std_obj.data).diff(periods=1).dropna()**2) / (std_obj.nrows - 1) )**0.5 / constants.c4_(std_obj.nrows)

 
# standard deviation within subgroups with subgroup size > 1
def _pooled_std(std_obj, **kwargs):
    """
    Calculate pooled standard deviation for pandas DataFrame columns.
    """

    # check if subgroup size is constant
    if len(set([x[~np.isnan(x)].size for x in std_obj.data])) == 1:
        # all subgroups have the same size
        # S_p = (sum([frame[col].var(skipna=True, ddof=1) for col in frame.columns]) / len(frame.columns)) ** 0.5
        # d = sum([frame[col].dropna(axis=0).size for col in frame.columns]) - len(frame.columns) + 1
        S_p = (sum([x[~np.isnan(x)].var(ddof=1) for x in std_obj.data]) / std_obj.nrows) ** 0.5
        d = sum([x[~np.isnan(x)].size for x in std_obj.data]) - std_obj.nrows + 1
        
    else:
        # calculate overall mean
        arr = std_obj.data.flatten()
        Xi_bar = arr[~np.isnan(arr)].mean()
        
        # S_p = (sum([sum((frame[col].dropna(axis=0)-Xi_bar)**2) for col in frame.columns]) / sum([(frame[col].dropna(axis=0).size - 1) for col in frame.columns])) ** 0.5
        # d = sum([(frame[col].dropna(axis=0).size - 1) for col in frame.columns]) + 1

        S_p = (sum([sum((x[~np.isnan(x)]-Xi_bar)**2) for x in std_obj.data]) / sum([(x[~np.isnan(x)].size - 1) for x in std_obj.data]) ) ** 0.5
        d = sum([(x[~np.isnan(x)].size - 1) for x in std_obj.data]) + 1

    return S_p / constants.c4(d)

def _r_bar(std_obj, columns=None, **kwargs):
    """
    Calculate r_bar; Average of subgroup ranges for pandas DataFrame columns.
    r_bar is used for estimating std_within when subgroup size > 1
        arguments
        frame:      Pandas Dataframe
        columns:    list of colums; if not provided all columns will be treated as subgroups

    std_within = sum_i ( (f_i * r_i) / (d2(n_i)) ) / sum_i (f_i)
    f_i = ( d2(n_i)**2 ) / ( d3(n_i)**2 )

    If all n_i are the same (all subgroup sizes are of equal length) then std_within is just the adjusted average of subgroup ranges.
    std_within = r_bar / d2(n_i)
    """
    
    # setup lambda functions
    subgroup_range = lambda x: (x.max() - x.min())
    f_i = lambda x: (constants.d2(x.size)**2) / (constants.d3(x.size)**2)

    # check if subgroup size is constant
    if len(set([x[~np.isnan(x)].size for x in std_obj.data])) == 1:
        # all subgroups have the same size
        # std_within = r_bar / d2(n_i)
        # std_within = (sum([subgroup_range(frame[col].dropna(axis=0)) for col in frame.columns]) / frame.shape[1])/ constants.d2(frame.shape[0])
        std_within = (sum([subgroup_range(x[~np.isnan(x)]) for x in std_obj.data]) / std_obj.nrows) / constants.d2(std_obj.ncols)
    else:
        # std_within = sum_i ( (f_i * r_i) / (d2(n_i)) ) / sum_i (f_i)
        # f_i = ( d2(n_i)**2 ) / ( d3(n_i)**2 )
        # std_within = sum([(f_i(frame[col]) * subgroup_range(frame[col])) / constants.d2(frame[col].size) for col in frame.columns])/sum([f_i(frame[col]) for col in frame.columns])
        std_within = sum([(f_i(x[~np.isnan(x)]) * subgroup_range(x[~np.isnan(x)])) / constants.d2(x.size) for x in std_obj.data]) / sum([f_i(x[~np.isnan(x)]) for x in std_obj.data])
    return std_within

def _s_bar(std_obj, **kwargs):
    """
    Calculate s_bar; Average of subgroup standard deviations for pandas DataFrame columns.
    s_bar is used for estimating std_within when subgroup size > 1
        arguments
        frame:      Pandas Dataframe
        columns:    list of colums; if not provided all columns will be treated as subgroups
    
    """
    
    # calculate overall mean
    arr = std_obj.data.flatten()
    Xi_bar = arr[~np.isnan(arr)].mean()

    # setup lambda functions
    s_i = lambda x: (sum( (x - Xi_bar)**2 ) / (x.size - 1) )**0.5
    h_i = lambda x: (constants.c4(x.size)**2) / (1 - (constants.c4(x.size)**2))
        
    # check if subgroup size is constant
    if len(set([x[~np.isnan(x)].size for x in std_obj.data])) == 1:
        # all subgroups have the same size
        # std_within = s_bar / c4(n_i)
        # std_within = (sum([frame[col].dropna(axis=0).std(ddof=0) for col in frame.columns]) / frame.shape[1]) / constants.c4(n_i)
        std_within = (sum([x[~np.isnan(x)].std(ddof=0) for x in std_obj.data]) / std_obj.nrows) / constants.c4(std_obj.ncols)
    else:
        # std_within = sum (h_i * s_i / c4(n_i)) / sum (h_i)
        # std_within = sum([(h_i(frame[col].dropna(axis=0)) * s_i(frame[col].dropna(axis=0))) / constants.c4(frame[col].dropna(axis=0).size) for col in frame.columns]) / sum(h_i(frame[col].dropna(axis=0)) for col in frame.columns)
        std_within = sum([(h_i(x[~np.isnan(x)]) * s_i(x[~np.isnan(x)])) / constants.c4(x.size) for x in std_obj.data]) / sum([h_i(x[~np.isnan(x)]) for x in std_obj.data])
    return std_within

