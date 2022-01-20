# -*- coding: utf-8 -*-
"""
Contains helper functions for plotting qa4sm results.
"""
from qa4sm_reader import globals

import numpy as np
import pandas as pd
import os.path

from typing import Union
import copy

import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcol
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch, PathPatch
from matplotlib.lines import Line2D

from cartopy import config as cconfig
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

from pygeogrids.grids import BasicGrid, genreg_grid
from shapely.geometry import Polygon, Point

import warnings

cconfig['data_dir'] = os.path.join(os.path.dirname(__file__), 'cartopy')


def _float_gcd(a, b, atol=1e-08):
    "Greatest common divisor (=groesster gemeinsamer teiler)"
    while abs(b) > atol:
        a, b = b, a % b
    return a


def _get_grid(a):
    "Find the stepsize of the grid behind a and return the parameters for that grid axis."
    a = np.unique(a)  # get unique values and sort
    das = np.unique(np.diff(a))  # get unique stepsizes and sort
    da = das[0]  # get smallest stepsize
    for d in das[1:]:  # make sure, all stepsizes are multiple of da
        da = _float_gcd(d, da)
    a_min = a[0]
    a_max = a[-1]
    len_a = int((a_max - a_min) / da + 1)
    return a_min, a_max, da, len_a


def _get_grid_for_irregulars(a, grid_stepsize):
    "Find the stepsize of the grid behind a for datasets with predeifned grid stepsize, and return the parameters for that grid axis."
    a = np.unique(a)
    a_min = a[0]
    a_max = a[-1]
    da = grid_stepsize
    len_a = int((a_max - a_min) / da + 1)
    return a_min, a_max, da, len_a


def _value2index(a, a_min, da):
    "Return the indexes corresponding to a. a and the returned index is a numpy array."
    return ((a - a_min) / da).astype('int')


def _format_floats(x):
    """Format floats in the statistsics table"""
    if isinstance(x, float):
        if abs(x) < 0.000001:
            return "0"
        elif 0.1 < abs(x) < 1e3:
            return np.format_float_positional(x, precision=2)
        else:
            return np.format_float_scientific(x, precision=2)
    else:
        return x


def oversample(lon, lat, data, extent, dx, dy):
    """Sample to regular grid"""
    other = BasicGrid(lon, lat)
    reg_grid = genreg_grid(dx, dy, minlat=extent[2], maxlat=extent[3],
                           minlon=extent[0], maxlon=extent[1])
    max_dist = dx * 111 * 1000  # a mean distance for one degree it's around 111 km
    lut = reg_grid.calc_lut(other, max_dist=max_dist)
    img = np.ma.masked_where(lut == -1, data[lut])
    img[np.isnan(img)] = np.ma.masked

    return img.reshape(-1, reg_grid.shape[1]), reg_grid


def geotraj_to_geo2d(df, index=globals.index_names, grid_stepsize=None):
    """
    Converts geotraj (list of lat, lon, value) to a regular grid over lon, lat.
    The values in df needs to be sampled from a regular grid, the order does not matter.
    When used with plt.imshow(), specify data_extent to make sure, 
    the pixels are exactly where they are expected.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'lat', 'lon' and 'var' Series.
    index : tuple, optional
        Tuple containing the names of lattitude and longitude index. Usually ('lat','lon')
        The default is globals.index_names
    grid_stepsize : None or float, optional
        angular grid stepsize to prepare a regular grid for plotting

    Returns
    -------
    zz : numpy.ndarray
        array holding the gridded values. When using plt.imshow, specify origin='lower'.
        [0,0] : llc (lower left corner)
        first coordinate is longitude.
    data_extent : tuple
        (x_min, x_max, y_min, y_max) in Data coordinates.
    origin : string
        'upper' or 'lower' - define how the plot should be oriented, for irregular grids it should return 'upper'
    """
    xx = df.index.get_level_values(index[1])  # lon
    yy = df.index.get_level_values(index[0])  # lat

    if grid_stepsize not in ['nan', None]:
        x_min, x_max, dx, len_x = _get_grid_for_irregulars(xx, grid_stepsize)
        y_min, y_max, dy, len_y = _get_grid_for_irregulars(yy, grid_stepsize)
        data_extent = (x_min - dx / 2, x_max + dx / 2, y_min - dy / 2, y_max + dy / 2)
        zz, grid = oversample(xx, yy, df.values, data_extent, dx, dy)
        origin = 'upper'
    else:
        x_min, x_max, dx, len_x = _get_grid(xx)
        y_min, y_max, dy, len_y = _get_grid(yy)
        ii = _value2index(yy, y_min, dy)
        jj = _value2index(xx, x_min, dx)
        zz = np.full((len_y, len_x), np.nan, dtype=np.float64)
        zz[ii, jj] = df
        data_extent = (x_min - dx / 2, x_max + dx / 2, y_min - dy / 2, y_max + dy / 2)
        origin = 'lower'

    return zz, data_extent, origin


def get_value_range(ds, metric=None, force_quantile=False, quantiles=[0.025, 0.975], diff_map=False):
    """
    Get the value range (v_min, v_max) from globals._metric_value_ranges
    If the range is (None, None), a symmetric range around 0 is created,
    showing at least the symmetric <quantile> quantile of the values.
    if force_quantile is True, the quantile range is used.

    Parameters
    ----------
    ds : pd.DataFrame or pd.Series
        Series holding the values
    metric : str , optional (default: None)
        name of the metric (e.g. 'R'). None equals to force_quantile=True.
    force_quantile : bool, optional
        always use quantile, regardless of globals.
        The default is False.
    quantiles : list, optional
        quantile of data to include in the range.
        The default is [0.025,0.975]
    diff_map : bool, default is False
        Whether the colorbar is for a difference plot

    Returns
    -------
    v_min : float
        lower value range of plot.
    v_max : float
        upper value range of plot.
    """
    if metric == None:
        force_quantile = True

    ranges = globals._metric_value_ranges
    if not force_quantile:  # try to get range from globals
        try:
            v_min = ranges[metric][0]
            v_max = ranges[metric][1]
            if (v_min is None and v_max is None):  # get quantile range and make symmetric around 0.
                v_min, v_max = get_quantiles(ds, quantiles)
                v_max = max(abs(v_min), abs(v_max))  # make sure the range is symmetric around 0
                v_min = -v_max
            elif v_min is None:
                v_min = get_quantiles(ds, quantiles)[0]
            elif v_max is None:
                v_max = get_quantiles(ds, quantiles)[1]
            else:  # v_min and v_max are both determinded in globals
                pass
        except KeyError:  # metric not known, fall back to quantile
            force_quantile = True
            warnings.warn('The metric \'{}\' is not known. \n'.format(metric) + \
                          'Could not get value range from globals._metric_value_ranges\n' + \
                          'Computing quantile range \'{}\' instead.\n'.format(str(quantiles)) +
                          'Known metrics are: \'' + \
                          '\', \''.join([metric for metric in ranges]) + '\'')

    if force_quantile:  # get quantile range
        v_min, v_max = get_quantiles(ds, quantiles)
        # adjust range based on the difference values in the map
        if diff_map:
            extreme = max([abs(v) for v in get_quantiles(ds, quantiles)])
            v_min, v_max = -extreme, extreme

    return v_min, v_max


def get_quantiles(ds, quantiles) -> tuple:
    """
    Gets lower and upper quantiles from pandas.Series or pandas.DataFrame

    Parameters
    ----------
    ds : (pandas.Series | pandas.DataFrame)
        Input values.
    quantiles : list
        quantile of values to include in the range

    Returns
    -------
    v_min : float
        lower quantile.
    v_max : float
        upper quantile.

    """
    q = ds.quantile(quantiles)
    if isinstance(ds, pd.Series):
        return q.iloc[0], q.iloc[1]
    elif isinstance(ds, pd.DataFrame):
        return min(q.iloc[0]), max(q.iloc[1])
    else:
        raise TypeError("Inappropriate argument type. 'ds' must be pandas.Series or pandas.DataFrame.")


def get_plot_extent(df, grid_stepsize=None, grid=False) -> tuple:
    """
    Gets the plot_extent from the values. Uses range of values and
    adds a padding fraction as specified in globals.map_pad

    Parameters
    ----------
    grid : bool
        whether the values in df is on a equally spaced grid (for use in mapplot)
    df : pandas.DataFrame
        Plot values.
    
    Returns
    -------
    extent : tuple | list
        (x_min, x_max, y_min, y_max) in Data coordinates.
    
    """
    lat, lon, gpi = globals.index_names
    if grid and grid_stepsize in ['nan', None]:
        # todo: problem if only single lon/lat point is present?
        x_min, x_max, dx, len_x = _get_grid(df.index.get_level_values(lon))
        y_min, y_max, dy, len_y = _get_grid(df.index.get_level_values(lat))
        extent = [x_min - dx / 2., x_max + dx / 2., y_min - dx / 2., y_max + dx / 2.]
    elif grid and grid_stepsize:
        x_min, x_max, dx, len_x = _get_grid_for_irregulars(df.index.get_level_values(lon), grid_stepsize)
        y_min, y_max, dy, len_y = _get_grid_for_irregulars(df.index.get_level_values(lat), grid_stepsize)
        extent = [x_min - dx / 2., x_max + dx / 2., y_min - dx / 2., y_max + dx / 2.]
    else:
        extent = [df.index.get_level_values(lon).min(), df.index.get_level_values(lon).max(),
                  df.index.get_level_values(lat).min(), df.index.get_level_values(lat).max()]
    dx = extent[1] - extent[0]
    dy = extent[3] - extent[2]
    # set map-padding around values to be globals.map_pad percent of the smaller dimension
    padding = min(dx, dy) * globals.map_pad / (1 + globals.map_pad)
    extent[0] -= padding
    extent[1] += padding
    extent[2] -= padding
    extent[3] += padding
    if extent[0] < -180:
        extent[0] = -180
    if extent[1] > 180:
        extent[1] = 180
    if extent[2] < -90:
        extent[2] = -90
    if extent[3] > 90:
        extent[3] = 90

    return extent


def init_plot(figsize, dpi, add_cbar=None, projection=None) -> tuple:
    """Initialize mapplot"""
    if not projection:
        projection = globals.crs
    fig = plt.figure(figsize=figsize, dpi=dpi)
    if add_cbar:
        gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[19, 1])
        ax = fig.add_subplot(gs[0], projection=projection)
        cax = fig.add_subplot(gs[1])
    else:
        gs = gridspec.GridSpec(nrows=1, ncols=1)
        ax = fig.add_subplot(gs[0], projection=projection)
        cax = None

    return fig, ax, cax


def get_extend_cbar(metric):
    """
    Find out whether the colorbar should extend, based on globals._metric_value_ranges[metric]

    Parameters
    ----------
    metric : str
        metric used in plot

    Returns
    -------
    str
        one of ['neither', 'min', 'max', 'both'].
    """
    vrange = globals._metric_value_ranges[metric]
    if vrange[0] is None:
        if vrange[1] is None:
            return 'both'
        else:
            return 'min'
    else:
        if vrange[1] is None:
            return 'max'
        else:
            return 'neither'


def style_map(
        ax, plot_extent, add_grid=True,
        map_resolution=globals.naturalearth_resolution,
        add_topo=False, add_coastline=True,
        add_land=True, add_borders=True, add_us_states=False,
        grid_intervals=globals.grid_intervals,
):
    """Parameters to style the mapplot"""
    ax.set_extent(plot_extent, crs=globals.data_crs)
    ax.spines["geo"].set_linewidth(0.4)
    if add_grid:
        # add gridlines. Bcs a bug in cartopy, draw girdlines first and then grid labels.
        # https://github.com/SciTools/cartopy/issues/1342
        try:
            grid_interval = max((plot_extent[1] - plot_extent[0]),
                                (plot_extent[3] - plot_extent[
                                    2])) / 5  # create apprx. 5 gridlines in the bigger dimension
            if grid_interval <= min(grid_intervals):
                raise RuntimeError
            grid_interval = min(grid_intervals, key=lambda x: abs(
                x - grid_interval))  # select the grid spacing from the list which fits best
            gl = ax.gridlines(crs=globals.data_crs, draw_labels=False,
                              linewidth=0.5, color='grey', linestyle='--',
                              zorder=3)  # draw only gridlines.
            # todo: this can slow the plotting down!!
            xticks = np.arange(-180, 180.001, grid_interval)
            yticks = np.arange(-90, 90.001, grid_interval)
            gl.xlocator = mticker.FixedLocator(xticks)
            gl.ylocator = mticker.FixedLocator(yticks)
        except RuntimeError:
            pass
        else:
            try:  # drawing labels fails for most projections
                gltext = ax.gridlines(crs=globals.data_crs, draw_labels=True,
                                      linewidth=0.5, color='grey', alpha=0., linestyle='-',
                                      zorder=4)  # draw only grid labels.
                xticks = xticks[(xticks >= plot_extent[0]) & (xticks <= plot_extent[1])]
                yticks = yticks[(yticks >= plot_extent[2]) & (yticks <= plot_extent[3])]
                gltext.xformatter = LONGITUDE_FORMATTER
                gltext.yformatter = LATITUDE_FORMATTER
                gltext.top_labels = False
                gltext.right_labels = False
                gltext.xlocator = mticker.FixedLocator(xticks)
                gltext.ylocator = mticker.FixedLocator(yticks)
            except RuntimeError as e:
                print("No tick labels plotted.\n" + str(e))
    if add_topo:
        ax.stock_img()
    if add_coastline:
        coastline = cfeature.NaturalEarthFeature('physical', 'coastline',
                                                 map_resolution,
                                                 edgecolor='black', facecolor='none')
        ax.add_feature(coastline, linewidth=0.4, zorder=3)
    if add_land:
        land = cfeature.NaturalEarthFeature('physical', 'land',
                                            map_resolution,
                                            edgecolor='none', facecolor='white')
        ax.add_feature(land, zorder=1)
    if add_borders:
        borders = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries',
                                               map_resolution,
                                               edgecolor='black', facecolor='none')
        ax.add_feature(borders, linewidth=0.2, zorder=3)
    if add_us_states:
        ax.add_feature(cfeature.STATES, linewidth=0.1, zorder=3)

    return ax


def make_watermark(
        fig,
        placement=globals.watermark_pos,
        for_map=False,
        offset=0.03
):
    """
    Adds a watermark to fig and adjusts the current axis to make sure there
    is enough padding around the watermarks.
    Padding can be adjusted in globals.watermark_pad.
    Fontsize can be adjusted in globals.watermark_fontsize.
    plt.tight_layout needs to be called prior to make_watermark,
    because tight_layout does not take into account annotations.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
    placement : str
        'top' : places watermark in top right corner
        'bottom' : places watermark in bottom left corner
    """
    # ax = fig.gca()
    # pos1 = ax.get_position() #fraction of figure
    fontsize = globals.watermark_fontsize
    pad = globals.watermark_pad
    height = fig.get_size_inches()[1]
    offset = offset + (((fontsize + pad) / globals.matplotlib_ppi) / height) * 2.2
    if placement == 'top':
        plt.annotate(globals.watermark, xy=[0.5, 1], xytext=[-pad, -pad],
                     fontsize=fontsize, color='grey',
                     horizontalalignment='center', verticalalignment='top',
                     xycoords='figure fraction', textcoords='offset points')
        top = fig.subplotpars.top
        fig.subplots_adjust(top=top - offset)
    elif placement == 'bottom':
        plt.annotate(globals.watermark, xy=[0.5, 0], xytext=[pad, pad],
                     fontsize=fontsize, color='grey',
                     horizontalalignment='center', verticalalignment='bottom',
                     xycoords='figure fraction', textcoords='offset points')
        bottom = fig.subplotpars.bottom
        if not for_map:
            fig.subplots_adjust(bottom=bottom + offset)
    else:
        raise NotImplementedError


def _make_cbar(fig, im, cax, ref_short: str, metric: str, label=None, diff_map=False):
    """
    Make colorbar to use in plots

    Parameters
    ----------
    fig: matplotlib.figure.Figure
        figure of plot
    im: AxesImage
        from method Axes.imshow()
    cax: axes.SubplotBase
        from fig.add_subplot
    ref_short: str
        name of ref dataset
    metric: str
        name of metric
    label: str
        label to describe the colorbar
    diff_map : bool, default is False
        Whether the colorbar is for a difference plot
    """
    if label is None:
        try:
            label = globals._metric_name[metric] + \
                    globals._metric_description[metric].format(
                        globals._metric_units[ref_short])
        except KeyError as e:
            raise Exception('The metric \'{}\' or reference \'{}\' is not known.\n'.format(metric, ref_short) + str(e))

    extend = get_extend_cbar(metric)
    if diff_map:
        extend = "both"
    cbar = fig.colorbar(im, cax=cax, orientation='horizontal', extend=extend)
    cbar.set_label(label, weight='normal')
    cbar.outline.set_linewidth(0.4)
    cbar.outline.set_edgecolor('black')
    cbar.ax.tick_params(width=0.4)

    return fig, im, cax


def _CI_difference(fig, ax, ci):
    """
    Insert the median value of the upper and lower CI difference

    Parameters
    ----------
    fig: matplotlib.figure.Figure
        figure with CIs
    ci: list
        list of upper and lower ci dataframes
    """
    lower_pos = []
    for ax in fig.axes:
        n = 0
        # iterating through axes artists:
        for c in ax.get_children():
            # searching for PathPatches
            if isinstance(c, PathPatch):
                # different width whether it's the metric or the CIs
                if n in np.arange(0, 100, 3):
                    # getting current width of box:
                    p = c.get_path()
                    verts = p.vertices
                    verts_sub = verts[:-1]
                    xmin = np.min(verts_sub[:, 0])
                    lower_pos.append(xmin)
                n += 1
    for ci_df, xmin in zip(ci, lower_pos):
        diff = ci_df["upper"] - ci_df["lower"]
        ci_range = float(diff.mean())
        ypos = float(ci_df["lower"].min())
        ax.annotate(
            "Mean CI\nRange:\n {:.2g}".format(ci_range),
            xy=(xmin - 0.2, ypos),
            horizontalalignment="center"
        )


def _add_dummies(df: pd.DataFrame, to_add: int) -> list:
    """
    Add empty columns in dataframe to avoid error in matplotlib when not all boxplot groups have the same
    number of values
    """
    for n, col in enumerate(np.arange(to_add)):
        # add columns while avoiding name clashes
        df[str(n)] = np.nan

    return df


def patch_styling(
        box_dict,
        facecolor
) -> None:
    """Define style of the boxplots"""
    for n, (patch, median) in enumerate(zip(box_dict["boxes"], box_dict["medians"])):
        patch.set(color="grey", facecolor=facecolor, linewidth=1.6, alpha=0.7)
        median.set(color="grey", linewidth=1.6)
    for (whis, caps) in zip(box_dict["whiskers"], box_dict["caps"]):
        whis.set(color="grey", linewidth=1.6)
        caps.set(color="grey", linewidth=1.6)


def _box_stats(ds: pd.Series, med: bool = True, iqrange: bool = True, count: bool = True) -> str:
    """
    Create the metric part with stats of the box (axis) caption

    Parameters
    ----------
    ds: pd.Series
        data on which stats are found
    med: bool
    iqrange: bool
    count: bool
        statistics

    Returns
    -------
    stats: str
        caption with summary stats
    """
    # interquartile range
    iqr = ds.quantile(q=[0.75, 0.25]).diff()
    iqr = abs(float(iqr.loc[0.25]))

    met_str = []
    if med:
        met_str.append('Median: {:.3g}'.format(ds.median()))
    if iqrange:
        met_str.append('IQR: {:.3g}'.format(iqr))
    if count:
        met_str.append('N: {:d}'.format(ds.count()))
    stats = '\n'.join(met_str)

    return stats


def boxplot(
        df,
        ci=None,
        label=None,
        figsize=None,
        dpi=100,
        spacing=0.35,
        axis=None,
        **plotting_kwargs,
) -> tuple:
    """
    Create a boxplot_basic from the variables in df.
    The box shows the quartiles of the dataset while the whiskers extend
    to show the rest of the distribution, except for points that are
    determined to be “outliers” using a method that is a function of
    the inter-quartile range.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'lat', 'lon' and (multiple) 'var' Series.
    ci : list
        list of Dataframes containing "upper" and "lower" CIs
    label : str, optional
        Label of the y axis, describing the metric. The default is None.
    figsize : tuple, optional
        Figure size in inches. The default is globals.map_figsize.
    dpi : int, optional
        Resolution for raster graphic output. The default is globals.dpi.
    spacing : float, optional.
        Space between the central boxplot and the CIs. Default is 0.3
    axis : matplotlib Axis obj.
        if provided, the plot will be shown on it

    Returns
    -------
    fig : matplotlib.figure.Figure
        the boxplot
    ax : matplotlib.axes.Axes
    """
    values = df.copy()
    center_pos = np.arange(len(values.columns)) * 2
    # make plot
    ax = axis
    if axis is None:
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ticklabels = values.columns
    # styling of the boxes
    kwargs = {"patch_artist": True, "return_type": "dict"}
    # changes necessary to have confidence intervals in the plot
    # could be an empty list or could be 'None', if de-selected from the kwargs
    if ci:
        upper, lower = [], []
        for n, intervals in enumerate(ci):
            lower.append(intervals["lower"])
            upper.append(intervals["upper"])
        lower = _add_dummies(
            pd.concat(lower, ignore_index=True, axis=1),
            len(center_pos) - len(ci),
        )
        upper = _add_dummies(
            pd.concat(upper, ignore_index=True, axis=1),
            len(center_pos) - len(ci),
        )
        low = lower.boxplot(
            positions=center_pos - spacing,
            showfliers=False,
            widths=0.15,
            ax=ax,
            **kwargs
        )
        up = upper.boxplot(
            positions=center_pos + spacing,
            showfliers=False,
            widths=0.15,
            ax=ax,
            **kwargs
        )
        patch_styling(low, 'skyblue')
        patch_styling(up, 'tomato')

    cen = values.boxplot(
        positions=center_pos,
        showfliers=False,
        widths=0.3,
        ax=ax,
        **kwargs
    )
    patch_styling(cen, 'white')
    if ci:
        low_ci = Patch(color='skyblue', alpha=0.7, label='Lower CI')
        up_ci = Patch(color='tomato', alpha=0.7, label='Upper CI')
        # _CI_difference(fig, ax, ci)
        plt.legend(
            handles=[low_ci, up_ci],
            fontsize=8,
            loc="best"
        )
    # provide y label
    if label is not None:
        plt.ylabel(label, weight='normal')
    ax.set_xticks(center_pos)
    ax.set_xticklabels(ticklabels)
    ax.tick_params(labelsize=globals.tick_size)
    ax.grid(axis='x')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    if axis is None:
        return fig, ax


# TODO: test?
def resize_bins(sorted, nbins):
    """Resize the bins for "continuous" metadata types"""
    bin_edges = np.linspace(0, 100, nbins + 1)
    p_rank = 100.0 * (np.arange(sorted.size) + 0.5) / sorted.size
    # use +- 1 to make sure nothing falls outside bins
    bin_edges = np.interp(bin_edges, p_rank, sorted, left=sorted[0] - 1, right=sorted[-1] + 1)
    bin_values = np.digitize(sorted, bin_edges)
    unique_values, counts = np.unique(bin_values, return_counts=True)
    bin_size = max(counts)

    return bin_values, unique_values, bin_size


def bin_continuous(
        df: pd.DataFrame,
        metadata_values: pd.DataFrame,
        meta_key: str,
        nbins=4,
        min_size=5,
        **kwargs,
) -> dict:
    """
    Subset the continuous metadata types

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of the values to plot
    metadata_values : pd.DataFrame
        metadata values
    meta_key : str
        name of the metadata
    nbins : int. Default is 4.
        Bins to divide the metadata range into
    min_size : int. Default is 5
        Minimum number of values to have in a bin
    kwargs: dict
        Keyword arguments for specific metadata types

    Returns
    -------
    binned: dict
        dictionary with metadata subsets as keys
    """
    meta_units = globals.metadata[meta_key][3]
    meta_range = metadata_values[meta_key].to_numpy()
    sorted = np.sort(meta_range)
    if len(meta_range) < min_size:
        raise ValueError(
            "There are too few points per metadata to generate the boxplots. You can set 'min_size'"
            "to a lower value to allow for smaller samples."
        )
    bin_values, unique_values, bin_size = resize_bins(sorted, nbins)
    # adjust bins to have the specified number of bins if possible, otherwise enough valoues per bin
    while bin_size < min_size:
        nbins -= 1
        bin_values, unique_values, bin_size = resize_bins(sorted, nbins)

    # use metadata to sort dataframe
    df = pd.concat([df, metadata_values], axis=1).sort_values(meta_key)
    df.drop(columns=meta_key, inplace=True)
    # put binned data in dataframe
    binned = {}
    for bin in unique_values:
        bin_index = np.where(bin_values == bin)
        bin_sorted = sorted[bin_index]
        bin_df = df.iloc[bin_index]
        bin_label = "{:.2f}-{:.2f} {}".format(min(bin_sorted), max(bin_sorted), meta_units)
        if not all(col >= min_size for col in bin_df.count()):
            continue
        binned[bin_label] = bin_df
    # If too few points are available to make the plots
    if not binned:
        return None

    return binned


def bin_classes(
        df: pd.DataFrame,
        metadata_values: pd.DataFrame,
        meta_key: str,
        min_size=5,
        **kwargs,
):
    """
    Subset the continuous metadata types

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of the values to plot
    metadata_values : pd.DataFrame
        metadata values
    meta_key : str
        name of the metadata
    min_size : int. Default is 5
        Minimum number of values to have in a bin
    kwargs: dict
        Keyword arguments for specific metadata types

    Returns
    -------
    binned: dict
        dictionary with metadata subsets as keys
    """
    classes_lut = globals.metadata[meta_key][1]
    grouped = metadata_values.applymap(
        lambda x: classes_lut[x]
    )
    binned = {}
    for meta_class, meta_df in grouped.groupby(meta_key).__iter__():
        bin_df = df.loc[meta_df.index]
        if not all(col >= min_size for col in bin_df.count()):
            continue
        binned[meta_class] = bin_df

    # If too few points are available to make the plots
    if not binned:
        return None

    return binned


def bin_discrete(
        df: pd.DataFrame,
        metadata_values: pd.DataFrame,
        meta_key: str,
        min_size=5,
        **kwargs,
) -> pd.DataFrame:
    """
    Provide a formatted dataframe for discrete type metadata (e.g. station or network)

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of the values to plot
    metadata_values : pd.DataFrame
        metadata values
    meta_key : str
        name of the metadata
    min_size : int. Default is 5
        Minimum number of values to have in a bin
    kwargs: dict
        Keyword arguments for specific metadata types

    Returns
    -------
    formatted: pd.DataFrame
        Dataframe formatted for seaborn plotting
    """
    groups = []
    for col in df.columns:
        group = pd.concat(
            [df[col], metadata_values],
            axis=1
        )
        group.columns = ["values", meta_key]
        group["Dataset"] = col
        groups.append(group)
    grouped = pd.concat(groups)
    formatted = []
    for meta, meta_df in grouped.groupby(meta_key).__iter__():
        if meta_df["values"].count() < min_size:
            continue
        formatted.append(meta_df)
    # If too few points are available to make the plots
    if not formatted:
        return None, None
    else:
        formatted = pd.concat(formatted)
        # return None as no CI data is needed for this plot
        return formatted


def bin_function_lut(type):
    """Lookup table between the metadata type and the binning function"""
    lut = {
        "continuous": bin_continuous,
        "discrete": bin_discrete,
        "classes": bin_classes,
    }
    if type not in lut.keys():
        raise KeyError(
            "The type '{}' does not correspond to any binning function".format(type)
        )

    return lut[type]


def _stats_discrete(df: pd.DataFrame, meta_key: str, stats_key: str) -> list:
    """Return list of stats by group, where groups are created with a specific key"""
    stats_list = []
    for _key, group in df.groupby(meta_key).__iter__():
        stats = _box_stats(group[stats_key])
        median = group[stats_key].median()
        stats_list.append((stats, median))

    return stats_list


def combine_soils(
        soil_fractions: dict,
        clay_fine: int = 35,
        clay_coarse: int = 20,
        sand_coarse: int = 65,
) -> pd.DataFrame:
    """
    Create a metadata granulometry classification based on 'coarse', 'medium' or 'fine' soil types. Uses
    the soil texture triangle diagram to transform the values.

    Parameters
    ----------
    soil_fractions: dict
        Dictionary with {'soil type (clay, sand or silt)': qa4sm_handlers.Metadata}
    clay_fine: int
        clay threshold above which the soil is fine
    clay_coarse: int
        clay threshold below which the soil can be coarse
    sand_coarse: int
        sand threshold above which the soil can be coarse

    Returns
    -------
    soil_combined: pd.DataFrame
        Dataframe with the new metadata type
    """
    # get thresholds on cartesian plane
    cf_y = clay_fine * np.sin(2 / 3 * np.pi)
    cc_y = clay_coarse * np.sin(2 / 3 * np.pi)
    sc_x = 100 - sand_coarse
    # transform values to cartesian
    x = soil_fractions["sand_fraction"].values.apply(lambda x: 100 - x)
    y = soil_fractions["clay_fraction"].values.apply(lambda x: x * np.sin(2 / 3 * np.pi))
    soil_combined = pd.concat([x, y], axis=1)
    soil_combined.columns = ["x", "y"]

    # function to calssify
    def sort_soil_type(row):
        if row["x"] < sc_x and row["y"] < cc_y:
            return "Coarse\ngranulometry"
        elif cc_y < row["y"] < cf_y:
            return "Medium\ngranulometry"
        else:
            return "Fine\ngranulometry"

    soil_combined = soil_combined.apply(lambda row: sort_soil_type(row), axis=1).to_frame("soil_type")

    return soil_combined


def combine_depths(depth_dict: dict) -> pd.DataFrame:
    """
    Create a metadata entry for the instrument depth by finding the middle point between the upper and lower
    specified instrument depths

    Parameters
    ----------
    depth_dict: dict
        Dictionary with {'instrument_depthfrom/instrument_depthto': qa4sm_handlers.Metadata}

    Returns
    -------
    depths_combined: pd.DataFrame
        Dataframe with the new metadata type
    """
    depths_combined = []
    for key, obj in depth_dict.items():
        depths_combined.append(obj.values)

    depths_combined = pd.concat(depths_combined, axis=1)
    depths_combined = depths_combined.mean(axis=1).to_frame("instrument_depth")

    return depths_combined


def aggregate_subplots(to_plot: dict, funct, n_bars, common_y=None, **kwargs):
    """
    Aggregate multiple subplots into one image

    Parameters
    ----------
    to_plot: dict
        dictionary with the data to plot, of the shape 'title of the subplot': pd.Dataframe
        (or data format required by funct)
    funct: method
        function to create the individual subplots. Should have a parameter 'axis',
        where the plt.Axis can be given. Returns a tuple of (unit_height, unit_width)
    n_bars: int
        number of boxplot bars (one is central + confidence intervals)
    **kwargs: dict
        arguments to pass on to the plotting function

    Return
    ------
    fig, axes
    """
    sub_n = len(to_plot.keys())
    if sub_n == 1:
        for n, (bin_label, data) in enumerate(to_plot.items()):
            fig, axes = funct(df=data, **kwargs)
    elif sub_n > 1:
        # provide the figure and subplots
        rows = int(np.ceil(sub_n / 2))
        fig, axes = plt.subplots(rows, 2, sharey=True)
        for n, (bin_label, data) in enumerate(to_plot.items()):
            if n % 2 == 0:
                try:
                    ax = axes[int(n / 2), 0]
                except IndexError:  # If only two subplots, it is a 1-dimensional array
                    ax = axes[0]
            else:
                try:
                    ax = axes[int(n / 2), 1]
                except IndexError:
                    ax = axes[1]
            # Make sure funct has the correct parameters format
            if 'axis' not in funct.__code__.co_varnames:
                raise KeyError(
                    "'axis' should be in the parameters of the given function {}".format(funct)
                )
            funct(df=data, axis=ax, **kwargs)
            ax.set_title(bin_label, fontdict={"fontsize": 10})
            if n != 0:
                ax.legend([], [], frameon=False)
        # eliminate extra subplot if odd number
        if rows * 2 > sub_n:
            fig.delaxes(axes[rows - 1, 1])

        plt.subplots_adjust(wspace=0.1, hspace=0.25)
        fig.set_figheight(globals.boxplot_height * (np.ceil(sub_n / 2) + 0.2))
        fig.set_figwidth(globals.boxplot_width * n_bars * 2)

        if common_y:
            fig.text(0.05, 0.5, common_y, va='center', rotation='vertical')

    return fig, axes


def bplot_multiple(to_plot, y_axis, n_bars, **kwargs) -> tuple:
    """
    Create subplots for each metadata category/range

    Parameters
    ----------
    to_plot : dict
        dictionary of {'bin name': Dataframe}
    y_axis : str
        Name of the x-axis
    n_bars : int or float
        Number of datasets/boxplot bars
    """
    # create plot with as many subplots as the dictionary keys
    n_subplots = len(to_plot.keys())

    if "axis" in kwargs.keys():
        del kwargs["axis"]

    fig, axes = aggregate_subplots(to_plot=to_plot, funct=boxplot, n_bars=n_bars, **kwargs)

    return fig, axes


def _dict2df(to_plot_dict: dict, meta_key: str) -> pd.DataFrame:
    """Transform a dictionary into a DataFrame for catplotting"""
    to_plot_df = []
    for range, values in to_plot_dict.items():
        range_grouped = []
        for ds in values:
            values_ds = values[ds].to_frame(name="values")
            values_ds["Dataset"] = ds
            values_ds[meta_key] = "\n[".join(range.split(" ["))
            range_grouped.append(values_ds)
        range_grouped = pd.concat(range_grouped)
        to_plot_df.append(range_grouped)
    to_plot_df = pd.concat(to_plot_df)

    return to_plot_df


def add_cat_info(to_plot: pd.DataFrame, metadata_name: str) -> pd.DataFrame:
    """Add info (N, median value) to metadata category labels"""
    groups = to_plot.groupby(metadata_name)["values"]
    counts = groups.count()
    to_plot[metadata_name] = to_plot[metadata_name].apply(
        lambda x: x + "\nN: {}".format(counts[x])
    )

    return to_plot


def bplot_catplot(to_plot, y_axis, metadata_name, axis=None, **kwargs) -> tuple:
    """
    Create individual plot with grouped boxplots by metadata value

    Parameters
    ----------
    to_plot: pd.Dataframe
        Seaborn-formatted dataframe
    y_axis: str
        Name of the x-axis
    metadata_name: str
        Name of the metadata type
    axis : matplotlib.axes.Axis, optional
        if provided, the function will create the plot on the specified axis
    """
    labels = None
    return_figax = False
    orient = "v"
    if axis is None:
        return_figax = True
        fig, axis = plt.subplots(1)
        orient = "h"

    if orient == "v":
        x = metadata_name
        y = "values"
    elif orient == "h":
        x = "values"
        y = metadata_name

    # add N points to the axis labels
    to_plot = add_cat_info(to_plot, metadata_name=metadata_name)

    box = sns.boxplot(
        x=x,
        y=y,
        hue="Dataset",
        data=to_plot,
        palette="Set2",
        ax=axis,
        showfliers=False,
        orient=orient,
    )
    n_bars = to_plot["Dataset"].nunique()
    n_meta = to_plot[metadata_name].nunique()
    unit_height = 1
    unit_width = len(to_plot[metadata_name].unique())
    # needed for overlapping station names
    box.tick_params(labelsize=globals.tick_size)
    dims = [globals.boxplot_width * n_meta * 2, globals.boxplot_height]
    if orient == "v":
        axis.set(xlabel=None, ylabel=y_axis)
        axis.yaxis.grid(True)  # Hide the horizontal gridlines
        axis.xaxis.grid(False)  # Show the vertical gridlines

    if orient == "h":
        axis.set(ylabel=None, xlabel=y_axis)
        axis.yaxis.grid(False)  # Hide the horizontal gridlines
        axis.xaxis.grid(True)  # Show the vertical gridlines

    axis.set_axisbelow(True)
    axis.spines['right'].set_visible(False)
    axis.spines['top'].set_visible(False)

    axis.legend(loc="best", fontsize="small")

    if return_figax:
        fig.set_figwidth(dims[0])
        fig.set_figheight(dims[1])

        return fig, axis

    else:
        axis.set(xlabel=None)
        axis.set(ylabel=None)


def boxplot_metadata(
        df: pd.DataFrame,
        metadata_values: pd.DataFrame,
        offset=0.02,
        ax_label=None,
        nbins=4,
        axis=None,
        plot_type: str = "catplot",
        **bplot_kwargs,
) -> tuple:
    """
    Boxplots by metadata. The output plot depends on the metadata type:

    - "continuous"
    - "discrete"
    - "classes"

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe with values for all variables (in metric)
    metadata_values : pd.DataFrame
        Dataframe containing the metadata values to use for the plot
    offset: float
        offset of watermark
    ax_label : str
        Name of the y axis - cannot be set globally
    nbins: int
        number pf bins to divide the plots in (only for continuous type of metadata, e.g. elevation)
    axis : matplotlib.axes.Axis, optional
        if provided, the function will create the plot on the specified axis
    plot_type : str, default is 'catplot'
        one of 'catplot' or 'multiplot', defines the type of plots for the 'classes' and 'continuous'
        metadata types

    Returns
    -------
    fig : matplotlib.figure.Figure
        the boxplot
    ax : matplotlib.axes.Axes
    labels : list
        list of class/ bins names
    """
    metric_label = "values"
    meta_key = metadata_values.columns[0]
    # sort data according to the metadata type
    type = globals.metadata[meta_key][2]
    bin_funct = bin_function_lut(type)
    to_plot = bin_funct(
        df=df,
        metadata_values=metadata_values,
        meta_key=meta_key,
        nbins=nbins,
    )
    if to_plot is None:
        raise ValueError(
            "There are too few points per metadata to generate the boxplots. You can set 'min_size'"
            "to a lower value to allow for smaller samples."
        )

    if isinstance(to_plot, dict):
        if plot_type == "catplot":
            to_plot = _dict2df(to_plot, meta_key)
            generate_plot = bplot_catplot
        elif plot_type == "multiplot":
            generate_plot = bplot_multiple

    elif isinstance(to_plot, pd.DataFrame):
        generate_plot = bplot_catplot

    out = generate_plot(
        to_plot=to_plot,
        y_axis=ax_label,
        metadata_name=meta_key,
        n_bars=len(df.columns),
        axis=axis,
        **bplot_kwargs,
    )

    if axis is None:
        fig, axes = out

        return fig, axes


def mapplot(
        df, metric,
        ref_short,
        ref_grid_stepsize=None,
        plot_extent=None,
        colormap=None,
        projection=None,
        add_cbar=True,
        label=None,
        figsize=globals.map_figsize,
        dpi=globals.dpi_min,
        diff_map=False,
        **style_kwargs
) -> tuple:
    """
        Create an overview map from df using values as color. Plots a scatterplot for ISMN and an image plot for other
        input values.

        Parameters
        ----------
        df : pandas.Series
            values to be plotted. Generally from metric_df[Var]
        metric : str
            name of the metric for the plot
        ref_short : str
                short_name of the reference dataset (read from netCDF file)
        ref_grid_stepsize : float or None, optional (None by default)
                angular grid stepsize, needed only when ref_is_angular == False,
        plot_extent : tuple or None
                (x_min, x_max, y_min, y_max) in Data coordinates. The default is None.
        colormap :  Colormap, optional
                colormap to be used.
                If None, defaults to globals._colormaps.
        projection :  cartopy.crs, optional
                Projection to be used. If none, defaults to globals.map_projection.
                The default is None.
        add_cbar : bool, optional
                Add a colorbar. The default is True.
        label : str, optional
            Label of the y-axis, describing the metric. If None, a label is autogenerated from metadata.
            The default is None.
        figsize : tuple, optional
            Figure size in inches. The default is globals.map_figsize.
        dpi : int, optional
            Resolution for raster graphic output. The default is globals.dpi.
        diff_map : bool, default is False
            if True, a difference colormap is created
        **style_kwargs :
            Keyword arguments for plotter.style_map().

        Returns
        -------
        fig : matplotlib.figure.Figure
            the boxplot
        ax : matplotlib.axes.Axes
        """
    if not colormap:
        cmap = globals._colormaps[metric]
    else:
        cmap = colormap
    v_min, v_max = get_value_range(df, metric)
    # everything changes if the plot is a difference map
    if diff_map:
        v_min, v_max = get_value_range(df, metric=None, diff_map=True)
        cmap = globals._diff_colormaps[metric]

    # mask values outside range (e.g. for negative STDerr from TCA)
    if metric in globals._metric_mask_range.keys():
        mask_under, mask_over = globals._metric_mask_range[metric]  # get values from scratch to disregard quantiles
        cmap = copy.copy(cmap)
        if mask_under is not None:
            v_min = mask_under
            cmap.set_under("red")
        if mask_over is not None:
            v_max = mask_over
            cmap.set_over("red")

    # initialize plot
    fig, ax, cax = init_plot(figsize, dpi, add_cbar, projection)

    # scatter point or mapplot
    if ref_short in globals.scattered_datasets:  # scatter
        if not plot_extent:
            plot_extent = get_plot_extent(df)

        markersize = globals.markersize ** 2
        lat, lon, gpi = globals.index_names
        im = ax.scatter(df.index.get_level_values(lon),
                        df.index.get_level_values(lat),
                        c=df, cmap=cmap, s=markersize,
                        vmin=v_min, vmax=v_max,
                        edgecolors='black', linewidths=0.1,
                        zorder=2, transform=globals.data_crs)
    else:  # mapplot
        if not plot_extent:
            plot_extent = get_plot_extent(df, grid_stepsize=ref_grid_stepsize, grid=True)
        if isinstance(ref_grid_stepsize, np.ndarray):
            ref_grid_stepsize = ref_grid_stepsize[0]
        zz, zz_extent, origin = geotraj_to_geo2d(df, grid_stepsize=ref_grid_stepsize)  # prep values
        im = ax.imshow(zz, cmap=cmap, vmin=v_min,
                       vmax=v_max, interpolation='nearest',
                       origin=origin, extent=zz_extent,
                       transform=globals.data_crs, zorder=2)

    if add_cbar:  # colorbar
        _make_cbar(fig, im, cax, ref_short, metric, label=label, diff_map=diff_map)
    style_map(ax, plot_extent, **style_kwargs)

    return fig, ax


def plot_spatial_extent(
        polys: dict,
        ref_points: bool = None,
        overlapping: bool = False,
        intersection_extent: tuple = None,
        reg_grid=False,
        grid_stepsize=None,
        **kwargs,
):
    """
    Plots the given Polygons and optionally the reference points on a map.

    Parameters
    ----------
    polys : dict
        dictionary with shape {name: shapely.geometry.Polygon}
    ref_points : 2D array of lon, lat for the reference points positions
    overlapping : bool, dafault is False.
        Whether the polygons have an overlap
    intersection_extent : tuple | None
        if given, corresponds to the extent of the intersection. Shape (minlon, maxlon, minlat, maxlat)
    reg_grid : bool, default is False,
        plotting oprion for regular grids (satellites)
    grid_stepsize:
    """
    fig, ax, cax = init_plot(figsize=globals.map_figsize, dpi=globals.dpi_min)
    legend_elements = []
    # plot polygons
    for n, items in enumerate(polys.items()):
        name, Pol = items
        if n == 0:
            union = Pol
        # get maximum extent
        union = union.union(Pol)
        style = {'color': 'powderblue', 'alpha': 0.4}
        # shade the union/intersection of the polygons
        if overlapping:
            x, y = Pol.exterior.xy
            if name == "selection":
                ax.fill(x, y, **style, zorder=5)
                continue
            ax.plot(x, y, label=name)
        # shade the areas individually
        else:
            if name == "selection":
                continue
            x, y = Pol.exterior.xy
            ax.fill(x, y, **style, zorder=6)
            ax.plot(x, y, label=name, zorder=6)
    # add reference points to the figure
    if ref_points is not None:
        if overlapping and intersection_extent is not None:
            minlon, maxlon, minlat, maxlat = intersection_extent
            mask = (ref_points[:, 0] >= minlon) & (ref_points[:, 0] <= maxlon) & \
                   (ref_points[:, 1] >= minlat) & (ref_points[:, 1] <= maxlat)
            selected = ref_points[mask]
            outside = ref_points[~ mask]
        else:
            selected, outside = ref_points, np.array([])
        marker_styles = [
            {"marker": "o", "c": "turquoise", "s": 15},
            {"marker": "o", "c": "tomato", "s": 15},
        ]
        # mapplot with imshow for gridded (non-ISMN) references
        if reg_grid:
            plot_df = []
            for n, (point_set, style, name) in enumerate(zip(
                    (selected, outside),
                    marker_styles,
                    ("Selected reference validation points", "Validation points outside selection")
            )):
                if point_set.size != 0:
                    point_set = point_set.transpose()
                    index = pd.MultiIndex.from_arrays(point_set, names=('lon', 'lat'))
                    point_set = pd.Series(
                        data=n,
                        index=index,
                    )
                    plot_df.append(point_set)
                    # plot point to 'fake' legend entry
                    ax.scatter(0, 0, label=name, marker="s", s=10, c=style["c"])
                else:
                    continue
            plot_df = pd.concat(plot_df, axis=0)
            zz, zz_extent, origin = geotraj_to_geo2d(
                plot_df,
                grid_stepsize=grid_stepsize
            )
            cmap = mcol.LinearSegmentedColormap.from_list('mycmap', ['turquoise', 'tomato'])
            im = ax.imshow(
                zz, cmap=cmap,
                origin=origin, extent=zz_extent,
                transform=globals.data_crs, zorder=4
            )
        # scatterplot for ISMN reference
        else:
            for point_set, style, name in zip(
                    (selected, outside),
                    marker_styles,
                    ("Selected reference validation points", "Validation points outside selection")
            ):
                if point_set.size != 0:
                    im = ax.scatter(
                        point_set[:, 0], point_set[:, 1],
                        edgecolors='black', linewidths=0.1,
                        zorder=4, transform=globals.data_crs,
                        **style, label=name
                    )
                else:
                    continue
    # style plot
    make_watermark(fig, globals.watermark_pos, offset=0)
    title_style = {"fontsize": 12}
    ax.set_title("Spatial extent of the comparison", **title_style)
    # provide extent of plot
    d_lon = abs(union.bounds[0] - union.bounds[2]) * 1 / 8
    d_lat = abs(union.bounds[1] - union.bounds[3]) * 1 / 8
    plot_extent = (union.bounds[0] - d_lon, union.bounds[2] + d_lon,
                   union.bounds[1] - d_lat, union.bounds[3] + d_lat)
    grid_intervals = [1, 5, 10, 30]
    style_map(ax, plot_extent, grid_intervals=grid_intervals)
    # create legend
    plt.legend(
        loc="lower left",
        fontsize='small',
        framealpha=0.4,
        edgecolor='black'
    )


def _res2dpi_fraction(res, units):
    # converts a certain validation resolution to a 0-1 fraction
    # indicating the output quality
    # equivalent min/max ranges for km and degrees based on
    # available datasets, approximated
    res_range = {
        "km": [1, 36],
        "deg": [0.01, 0.33],
    }

    fraction = (res - min(res_range[units])) / (max(res_range[units]) - min(res_range[units]))

    return (1 - fraction)**2


def _extent2dpi_fraction(extent):
    # converts a certain validation extent to a 0-1 fraction
    # indicating the output quality
    max_extent = 360 * 110
    actual_extent = (extent[1]-extent[0]) * (extent[3]-extent[2])

    return actual_extent / max_extent


def output_dpi(
        res,
        units,
        extent,
        dpi_min=globals.dpi_min,
        dpi_max=globals.dpi_max
) -> float:
    # get ouput dpi based on image extent and validation resolution
    # dpi = SQRT(extent_coeff^2 + res_coeff^2)
    dpi_vec = _extent2dpi_fraction(extent)**2 + _res2dpi_fraction(res, units)**2
    dpi_vec = np.sqrt(dpi_vec)
    dpi_fraction = dpi_vec / np.sqrt(2)

    dpi = dpi_min + (dpi_max-dpi_min) * dpi_fraction

    return float(dpi)
