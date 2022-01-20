import re
import math
from decimal import Decimal

import numpy as np
import pandas as pd
from scipy.stats import distributions

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import groupby

# matplotlib format
def _axisformat(ax, series):

    if isinstance(series.index, pd.DatetimeIndex):
        rng = series.index.max() - series.index.min()

        if rng > pd.Timedelta('365 days'):
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%Y'))
            ax.set_xlabel('month')
        elif rng > pd.Timedelta('183 days'):
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.set_xlabel('month')
        elif rng > pd.Timedelta('31 days'):
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%V'))
            ax.set_xlabel('week')
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
            ax.set_xlabel('date')
    elif isinstance(series, pd.DataFrame):
        ax.set_xlabel(series.iloc[:,0].name)
        ax.set_ylabel(series.index.name)
    else:
        ax.set_xlabel(series.name)

    return ax

def _get_multiindex_labels(ax, _obj, style):
    # great thanks to Trenton McKinney
    # https://stackoverflow.com/questions/19184484/how-to-add-group-labels-for-bar-charts-in-matplotlib

    def _add_line(ax, xpos, ypos):
        line = plt.Line2D([xpos, xpos], [ypos + .025, ypos], transform=ax.transAxes, **style.graphs.line.multiindex_label_line)
        line.set_clip_on(False)
        ax.add_line(line)

    def _get_label_len(my_index,level):
        labels = my_index.get_level_values(level)
        return [(k, sum(1 for i in g)) for k,g in groupby(labels)]

    # remove current labels
    ax.set_xticklabels([])
    ax.set_xlabel('')

    # draw new labels
    ypos = -.025
    
    # margins
    xmargins = 2 * ax.margins()[0]

    scale = (1.-xmargins)/(_obj.index.size - 1)
    for level in range(_obj.index.nlevels)[::-1]:
        pos = 0
        for label, rpos in _get_label_len(_obj.index,level):
            #lxpos = ((pos + .5 * rpos)*scale) + ax.margins()[0]
            #ax.text(lxpos, ypos, label, ha='center', transform=ax.transAxes)
            _add_line(ax, (pos*scale) + ax.margins()[0], ypos)
            pos += rpos
        #_add_line(ax, (pos*scale) + ax.margins()[0] , ypos)
        ypos -= .1


def _get_multiindex_labels_old(ax, _obj, style):
    # great thanks to Trenton McKinney
    # https://stackoverflow.com/questions/19184484/how-to-add-group-labels-for-bar-charts-in-matplotlib

    def _add_line(ax, xpos, ypos):
        line = plt.Line2D([xpos, xpos], [ypos + .1, ypos], transform=ax.transAxes, **style.graphs.line.multiindex_label_line)
        line.set_clip_on(False)
        ax.add_line(line)

    def _get_label_len(my_index,level):
        labels = my_index.get_level_values(level)
        return [(k, sum(1 for i in g)) for k,g in groupby(labels)]

    # remove current labels
    ax.set_xticklabels([])
    ax.set_xlabel('')

    # draw new labels
    ypos = -.1
    #
    #
    #
    #
    scale = (1.-(2 * ax.margins()[0]))/_obj.index.size
    #scale = 1./_obj.index.size
    for level in range(_obj.index.nlevels)[::-1]:
        #
        #
        #
        pos = 0
        #
        #
        #
        # pos = 0
        for label, rpos in _get_label_len(_obj.index,level):
            lxpos = ((pos + .5 * rpos)*scale) + ax.margins()[0]
            ax.text(lxpos, ypos, label, ha='center', transform=ax.transAxes)
            _add_line(ax, (pos*scale) + ax.margins()[0], ypos)
            pos += rpos
        _add_line(ax, (pos*scale) + ax.margins()[0] , ypos)
        ypos -= .1


def _set_x_axis(ax, _obj):
    # set the x axis, depending on the index data type


    # xticks
    # if isinstance(_obj.series.index, pd.MultiIndex):
    #     bluebelt.graph.helpers._get_multiindex_labels(ax1, _obj.series, style)
    #     fig.subplots_adjust(bottom=.1*_obj.series.index.nlevels)
    # elif isinstance(_obj.series.index, pd.DatetimeIndex):
    #     bluebelt.graph.helpers._axisformat(ax1, _obj.series)
    
    
    #bluebelt.graph.helpers._axisformat(ax1, _obj.series)


    return 