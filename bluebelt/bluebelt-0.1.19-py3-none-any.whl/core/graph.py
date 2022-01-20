import pandas as pd
import numpy as np
import scipy.stats as stats

import bluebelt.styles
import bluebelt.core.helpers

import warnings

def line(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.line)

def dotted_line(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.dotted_line)

def dashed_line(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.dashed_line)
    
def fill_between(index, lower, upper, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.fill_between(index, lower, upper, label=label, **kwargs, **style.default.fill_between)

def scatter(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.scatter)
    
def observations(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.observations)
    
def out_of_bounds(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.out_of_bounds)

def outliers(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.plot(index, values, label=label, **kwargs, **style.default.outliers)

def area(index, values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.stackplot(index, values, **kwargs, **style.default.area)
    ax.plot(index, values, label=label, **kwargs, **style.default.line)

def hist(values, ax, label=None, **kwargs):
    style = kwargs.pop('style', bluebelt.styles.paper)
    ax.hist(values, **kwargs, label=label, **style.default.hist) 

# def boxplot(series, ax, **kwargs):

#     # get data
#     if isinstance(series, (pd.Series, pd.DataFrame))and series.isnull().values.any():
#         warnings.warn('the series contains Null values which will be removed', Warning)
#         series = series.dropna()

#     style = kwargs.pop('style', bluebelt.styles.paper)
        
#     boxplot = ax.boxplot(series)

#     for box in boxplot['boxes']:
#         # add style if any is given
#         box.set(**style.graphs.boxplot.boxplot.get('boxes', {}))
