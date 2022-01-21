# -*- coding: utf-8 -*-
r"""
This module contains utilities for visualizations of spin configurations.
"""
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
import numpy as np


def truncate_colormap(cmap, minval: float = 0.0, maxval: float = 1.0, n: int = 100):
    r"""
    Returns:
        A new colormap which is a segment of a known color map in matplotlib
    """
    return colors.LinearSegmentedColormap.from_list(
        'trunc({c},{a:.2f},{b:.2f})'.format(c=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))


def get_colormap(which: str = 'hsv_spind') -> mpl.colors.LinearSegmentedColormap:
    r"""
    Returns:
        the desired colormap based on a key string.
    """
    if which == 'hsv_spind':
        mpl.cm.register_cmap('hsv_new', cmap=truncate_colormap(mpl.cm.get_cmap('hsv'), minval=0.6, maxval=0.0))
        return mpl.cm.get_cmap('hsv_new')
    elif which == 'paraview_standard':
        return mpl.cm.get_cmap('viridis')
    elif which == 'coolwarm':
        return mpl.cm.get_cmap('coolwarm')
