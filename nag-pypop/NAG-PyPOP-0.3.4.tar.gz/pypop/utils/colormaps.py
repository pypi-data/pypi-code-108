#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause-Clear
# Copyright (c) 2019, The Numerical Algorithms Group, Ltd. All rights reserved.

from matplotlib.colors import LinearSegmentedColormap

__all__ = ["build_efficiency_colormap", "build_inefficiency_colormap"]


def build_efficiency_colormap(good_thres=0.8, bad_thres=0.5, name="POP Eff "):
    """Build a Red-Green colormap for metric representation

    Parameters
    ----------
    good_thres: float (0,1]
        Threshold for color to switch from red (below) to green (above)
    bad_thres: float [0,1)
        Threshold below which color is solid red (alpha=1)
    name: str
        Unique name for the colormap for internal tracking by matplotlib
    """

    cmap_points = [
        (0.0, (0.690, 0.074, 0.074)),
        (bad_thres, (0.690, 0.074, 0.074)),
        (good_thres - 1e-5, (0.992, 0.910, 0.910)),
        (good_thres, (0.910, 0.992, 0.910)),
        (1.0, (0.074, 0.690, 0.074)),
    ]

    return LinearSegmentedColormap.from_list(name, colors=cmap_points, N=256, gamma=1)


def build_inefficiency_colormap(good_thres=0.8, bad_thres=0.5, name="POP Ineff"):
    """Build a Green-Red colormap for metric representation

    Parameters
    ----------
    good_thres: float [0,1)
        Threshold for color to switch from green (below) to red (above)
    bad_thres: float (0,1]
        Threshold above which color is solid red (alpha=1)
    name: str
        Unique name for the colormap for internal tracking by matplotlib
    """

    cmap_points = [
        (0.0, (0.074, 0.690, 0.074)),
        (good_thres, (0.910, 0.992, 0.910)),
        (good_thres + 1e-5, (0.992, 0.910, 0.910)),
        (bad_thres, (0.690, 0.074, 0.074)),
        (1.0, (0.690, 0.074, 0.074)),
    ]

    return LinearSegmentedColormap.from_list(name, colors=cmap_points, N=256, gamma=1)
