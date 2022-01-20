import pandas as pd
import matplotlib.pyplot as plt

import bluebelt.core.graph_old
import bluebelt.core.helpers



def _get_frame(_obj, **kwargs):

    columns = kwargs.get('columns', None)

    if isinstance(_obj, pd.DataFrame) and isinstance(columns, (str, list)):
        return _obj[columns]
    elif isinstance(_obj, pd.Series):
        return pd.DataFrame(_obj)
    else:
        return _obj

def _get_name(_obj, **kwargs):

    if isinstance(_obj, pd.Series):
        return _obj.name
    elif isinstance(_obj, pd.DataFrame):
        names = []
        for col in _obj.columns:
            names.append(col)
        return bluebelt.core.helpers._get_nice_list(names)
    else:
        return None
    
def line(_obj, **kwargs):
    """
    Make a line plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """

    style = kwargs.pop('style', bluebelt.styles.paper)
    _func = _obj._blue_function + ' ' if hasattr(_obj, '_blue_function') else ''
    title = kwargs.pop('title', f'{_get_name(_obj)} {_func}line plot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    frame = _get_frame(_obj, **kwargs)

    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    for col in frame:
        # _obj.plot(kind='line', ax=fig.gca())
        # bluebelt.core.graph.line(series=frame[col], ax=axes, style=style)
        axes.plot(frame[col].values, **style.graphs.line.plot, label=col)
    
    
    # xticks
    if isinstance(frame.index, pd.MultiIndex):
        bluebelt.core.helpers._get_multiindex_labels(axes, _obj, style)
        fig.subplots_adjust(bottom=.1*_obj.index.nlevels)
    elif isinstance(frame.index, pd.DatetimeIndex):
        bluebelt.core.helpers._axisformat(axes, _obj)
    
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # legend
    if isinstance(_obj, pd.DataFrame):
        if _obj.shape[1] > 1:
            axes.legend(loc='best')
    # title
    axes.set_title(title, **style.graphs.line.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig


def scatter(_obj, **kwargs):
    """
    Make a scatter plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    style = kwargs.pop('style', bluebelt.styles.paper)
    _func = _obj._blue_function + ' ' if hasattr(_obj, '_blue_function') else ''
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    frame = _get_frame(_obj, **kwargs)

    if frame.shape[1] >= 2:
        title = kwargs.pop('title', f'{_get_name(frame.iloc[:,:2])}  {_func}scatter plot')
        index_name = frame.columns[0]
        frame = pd.DataFrame(data={frame.columns[1]: frame.iloc[:,1].values}, index=frame.iloc[:,0].values)
        frame.index.name = index_name
    else:
        title = kwargs.pop('title', f'{_get_name(_obj)}  {_func}scatter plot')
    
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    bluebelt.core.graph_old.scatter(series=frame, ax=axes, style=style)
        
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.scatter.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

def area(_obj, **kwargs):
    """
    Make an area plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    
    frame = _get_frame(_obj, **kwargs)

    style = kwargs.pop('style', bluebelt.styles.paper)
    _func = _obj._blue_function + ' ' if hasattr(_obj, '_blue_function') else ''
    title = kwargs.pop('title', f'{_get_name(_obj)} {_func}area plot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    for col in frame:
        # .get_level_values(-1) hack to get last level
        axes.stackplot(list(frame[col].index.get_level_values(-1)), frame[col].values, **style.graphs.area.stackplot)
        axes.plot(list(frame[col].index.get_level_values(-1)), frame[col].values, label=col, **style.graphs.area.plot, **kwargs)
        
    # xticks
    if isinstance(frame.index, pd.MultiIndex):
        bluebelt.core.helpers._get_multiindex_labels(axes, _obj, style)
        fig.subplots_adjust(bottom=.1*_obj.index.nlevels)
    elif isinstance(frame.index, pd.DatetimeIndex):
        bluebelt.core.helpers._axisformat(axes, _obj)
    
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # legend
    if isinstance(_obj, pd.DataFrame):
        if _obj.shape[1] > 1:
            axes.legend(loc='best')
    
    # title
    axes.set_title(title, **style.graphs.area.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

def hist(_obj, **kwargs):
    """
    Make a histogram plot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        fit: boolean
            fit a normal distribution
            default value: False
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    
    frame = _get_frame(_obj, **kwargs)

    style = kwargs.pop('style', bluebelt.styles.paper)
    _func = _obj._blue_function + ' ' if hasattr(_obj, '_blue_function') else ''
    title = kwargs.pop('title', f'{_get_name(_obj)} {_func}histogram')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    for col in frame:
        # .get_level_values(-1) hack to get last level
        axes.hist(frame[col], label=col, **style.default.hist) 
        
        #bluebelt.core.graph_old.hist(series=series, ax=axes, style=style, fit=fit)
        
    # format things
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    
    # title
    axes.set_title(title, **style.graphs.area.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig

histogram = hist

def boxplot(_obj, **kwargs):
    """
    Make a boxplot for a pandas Series or a pandas Dataframe
        arguments
        _obj: pandas.Series or pandas.Dataframe
        style: bluebelt style
            default value: bluebelt.styles.paper
        title: string
            default value: pandas Series name or pandas Dataframe column names
        path: string
            the full path to save the plot (e.g. 'results/plot_001.png')
            default value: None
        xlim: tuple
            a tuple with the two limits for the x-axis (e.g. (0, 100) or (None, 50))
            default value: (None, None)
        ylim: tuple
            a tuple with the two limits for the y-axis (e.g. (0, None) or (100, 200))
            default value: (None, None)
        **kwargs: all additional kwargs will be passed to matplotlib.pyplot.subplots()
    """
    
    style = kwargs.pop('style', bluebelt.styles.paper)
    _func = _obj._blue_function + ' ' if hasattr(_obj, '_blue_function') else ''
    title = kwargs.pop('title', f'{_get_name(_obj)} {_func}boxplot')
    
    path = kwargs.pop('path', None)
    xlim = kwargs.pop('xlim', (None, None))
    ylim = kwargs.pop('ylim', (None, None))
    
    frame = _get_frame(_obj, **kwargs)

    # prepare figure
    fig, axes = plt.subplots(nrows=1, ncols=1, **kwargs)

    bluebelt.core.graph_old.boxplot(series=frame.values, ax=axes, style=style)
        
    # format things
    axes.set_xticklabels(frame.columns)
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
            
    # title
    axes.set_title(title, **style.graphs.boxplot.title)

    if path:
        plt.savefig(path)
        plt.close()
    else:
        plt.close()
        return fig
    