import pandas as pd
import scipy.stats as stats

import matplotlib.pyplot as plt

import bluebelt.statistics.hypothesis_testing

import bluebelt.styles

class WeekDay(): 
    """
    Compare the distribution of data between week days
        arguments
        series: pandas.Series
            the Series must have a pandas.DatetimeIndex
        
        properties
        .series
            the transformed pandas.Series with week day index
        .data
            the data
        .equal_means
            the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
        .equal_variances
            the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

        methods
        .plot()
            plot the results as a boxplot
    """
    

    def __init__(self, series, **kwargs):
        
        self.series = series
        self.name = series.name
        self.calculate()

    def calculate(self):
        self.series = pd.Series(index=[self.series.index.weekday, self.series.index.day_name()], data=self.series.values, name=self.series.name).sort_index(level=0).droplevel(0)
        
        _calculate(self)
        
        
    def __repr__(self):
        return (f'{self.__class__.__name__}(series={self.name!r}, equal_means={self.equal_means}, equal_variances={self.equal_variances})')

    def plot(self, **kwargs):
        return _datetime_plot(self, title=f'{self.name} week day distribution', **kwargs)
        
class MonthDay():  
    """
    Compare the distribution of data between month days
        arguments
        series: pandas.Series
            the Series must have a pandas.DatetimeIndex
        
        properties
        .series
            the transformed pandas.Series with month day index
        .data
            the data
        .equal_means
            the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
        .equal_variances
            the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

        methods
        .plot()
            plot the results as a boxplot
    """

    def __init__(self, series, **kwargs):
        
        self.series = series
        self.name = series.name
        self.calculate()

    def calculate(self):
        
        self.series = pd.Series(index=self.series.index.day, data=self.series.values, name=self.series.name).sort_index()
        
        _calculate(self)
                
    def __repr__(self):
        return (f'{self.__class__.__name__}(series={self.name!r}, equal_means={self.equal_means}, equal_variances={self.equal_variances})')

    def plot(self, **kwargs):
        return _datetime_plot(self, title=f'{self.name} month day distribution', **kwargs) 

class Week(): 
    """
    Compare the distribution of data between weeks
        arguments
        series: pandas.Series
            the Series must have a pandas.DatetimeIndex
        
        properties
        .series
            the transformed pandas.Series with week number index
        .data
            the data
        .equal_means
            the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
        .equal_variances
            the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

        methods
        .plot()
            plot the results as a boxplot
    """
    
    def __init__(self, series, **kwargs):
        
        self.series = series
        self.name = series.name
        self.calculate()

    def calculate(self):
        
        self.series = pd.Series(index=self.series.index.isocalendar().week, data=self.series.values, name=self.series.name).sort_index()
        
        _calculate(self)

    def __repr__(self):
        return (f'{self.__class__.__name__}(series={self.name!r}, equal_means={self.equal_means}, equal_variances={self.equal_variances})')

    def plot(self, **kwargs):
        return _datetime_plot(self, title=f'{self.name} week distribution', **kwargs)
        
class Month():
    """
    Compare the distribution of data between months
        arguments
        series: pandas.Series
            the Series must have a pandas.DatetimeIndex
        
        properties
        .series
            the transformed pandas.Series with month index
        .data
            the data
        .equal_means
            the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
        .equal_variances
            the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

        methods
        .plot()
            plot the results as a boxplot
    """
    
    def __init__(self, series, **kwargs):
        
        self.series = series
        self.name = series.name
        self.calculate()

    def calculate(self):
        
        self.series = pd.Series(index=self.series.index.month, data=self.series.values, name=self.series.name).sort_index()
       
        _calculate(self)
                
    def __repr__(self):
        return (f'{self.__class__.__name__}(series={self.name!r}, equal_means={self.equal_means}, equal_variances={self.equal_variances})')

    def plot(self, **kwargs):
        return _datetime_plot(self, title=f'{self.name} month distribution', **kwargs)
        
class Year():
    """
    Compare the distribution of data between years
        arguments
        series: pandas.Series
            the Series must have a pandas.DatetimeIndex
        
        properties
        .series
            the transformed pandas.Series with year index
        .data
            the data
        .equal_means
            the result of bluebelt.statistics.hypothesis_testing.EqualMeans().passed
        .equal_variances
            the result of bluebelt.statistics.hypothesis_testing.EqualVariances().passed

        methods
        .plot()
            plot the results as a boxplot
    """
    
    def __init__(self, series, **kwargs):
        
        self.series = series
        self.name = series.name
        self.calculate()

    def calculate(self):
        
        self.series = pd.Series(index=self.series.index.year, data=self.series.values, name=self.series.name).sort_index()
        
        _calculate(self)
                
    def __repr__(self):
        return (f'{self.__class__.__name__}(series={self.name!r}, equal_means={self.equal_means}, equal_variances={self.equal_variances})')

    def plot(self, **kwargs):
        return _datetime_plot(self, title=f'{self.name} year distribution')


def _calculate(dt_obj, **kwargs):

    dt_obj.frame = pd.DataFrame.from_dict({i:pd.Series(dt_obj.series[i]).to_list() for i in dt_obj.series.index.unique()}, orient='index').T    
    dt_obj.means = dt_obj.frame.mean() #{key:value for key, value in zip(dt_obj.series.index.unique(), pd.DataFrame(dt_obj.data).mean(axis=1).values)}
    dt_obj.variances = dt_obj.frame.var() #{key:value for key, value in zip(dt_obj.series.index.unique(), pd.DataFrame(dt_obj.data).var(axis=1).values)}
    dt_obj.equal_means = bluebelt.statistics.hypothesis_testing.EqualMeans(dt_obj.frame).passed
    dt_obj.equal_variances = bluebelt.statistics.hypothesis_testing.EqualVariances(dt_obj.frame).passed
    
    normal_distribution_test = bluebelt.statistics.hypothesis_testing.NormalDistribution(dt_obj.frame)

    dt_obj.normal_distribution = normal_distribution_test.passed_values
    dt_obj.normal_distribution_p_values = normal_distribution_test.p_values
        

def _datetime_plot(plot_obj, **kwargs):
        
    title = kwargs.pop('title', f'{plot_obj.name} datetime distribution')
    style = kwargs.pop('style', bluebelt.styles.paper)
    
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    path = kwargs.pop('path', None)        
    
    # prepare figure
    fig, ax = plt.subplots(**kwargs)

    boxplot = ax.boxplot([plot_obj.frame[col].dropna() for col in plot_obj.frame])

    for n, box in enumerate(boxplot['boxes']):
        # add style if any is given
        box.set(**style.graphs.boxplot.boxplot.get('boxes', {}))
        
    # title
    ax.set_title(title, **style.graphs.boxplot.title)

    # labels        
    ax.set_xticklabels(plot_obj.series.index.unique())

    # set limits
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig