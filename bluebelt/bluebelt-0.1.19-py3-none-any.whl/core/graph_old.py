import pandas as pd
import numpy as np
import scipy.stats as stats

import bluebelt.styles
import bluebelt.core.helpers

import warnings

def line(series, ax, **kwargs):

    # handle kwargs
    style = kwargs.pop('style', bluebelt.styles.paper)
    label = kwargs.pop('label', None)

    # area plot
    ax.plot(series, **style.graphs.line.plot, label=label)
    
    # set x axis locator
    #bluebelt.core.helpers._axisformat(ax, series)
    #ax.set_ylim(0,)

def scatter(series, ax, **kwargs):

    # handle kwargs
    style = kwargs.pop('style', bluebelt.styles.paper)
    
    # area plot
    ax.plot(series, **style.graphs.scatter.plot)
    
    # set x axis locator
    bluebelt.core.helpers._axisformat(ax, series)
    ax.set_ylim(0,)

def area(series, ax, **kwargs):

    # handle kwargs
    style = kwargs.pop('style', bluebelt.styles.paper)
    
    # area plot
    ax.stackplot(series.index, series.values, **style.graphs.area.stackplot)
    ax.plot(series, **style.graphs.area.plot, **kwargs)
    
    # set x axis locator
    bluebelt.core.helpers._axisformat(ax, series)
    ax.set_ylim(0,)

def hist(series, ax, fit=False, **kwargs):

    # handle kwargs
    style = kwargs.pop('style', bluebelt.styles.paper)
    
    # histogram
    ax.hist(series, **style.graphs.hist.hist)
    ax.set_yticks([])

    # fit a normal distribution to the data
    if fit:
        norm_mu, norm_std = stats.norm.fit(series.dropna())
        xlims = ax.get_xlim()
        pdf_x = np.linspace(xlims[0], xlims[1], 100)
        ax.plot(pdf_x, stats.norm.pdf(pdf_x, norm_mu, norm_std), **style.graphs.hist.normal_plot)


def boxplot(series, ax, **kwargs):

    # get data
    if isinstance(series, (pd.Series, pd.DataFrame))and series.isnull().values.any():
        warnings.warn('the series contains Null values which will be removed', Warning)
        series = series.dropna()

    style = kwargs.pop('style', bluebelt.styles.paper)
        
    boxplot = ax.boxplot(series)

    for box in boxplot['boxes']:
        # add style if any is given
        box.set(**style.graphs.boxplot.boxplot.get('boxes', {}))
