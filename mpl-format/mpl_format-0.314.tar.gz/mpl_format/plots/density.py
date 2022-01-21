import matplotlib.pyplot as plt
from numpy import log10, inf
from typing import Optional, List, Union, Tuple

from matplotlib.axes import Axes
from numpy import concatenate
from pandas import DataFrame, cut

from mpl_format.axes import AxesFormatter
from mpl_format.axes.axis_utils import new_axes
from mpl_format.compound_types import Color


def categorical_discrete_values_histogram(
        data: DataFrame,
        x: str, y: str,
        categories: Optional[List[str]] = None,
        colors: Union[Color, List[Color]] = 'k',
        norm: str = 'single',
        mean: Optional[Color] = None,
        median: Optional[Color] = None,
        ax: Optional[Axes] = None
):
    """
    Plot a histogram of several categories together.

    :param data: DataFrame with columns x and y
    :param x: Name of the category column. Categories will be found from the
              unique values of this column.
    :param y: Name of the value column. Each value is assumed to be a count,
              and the number of each count value will be counted.
    :param categories: Optional override for categories of x. Use to select a
                       subset of x, or to reorder x.
    :param colors: Single color or list of colors to override default color of
                   each histogram.
    :param norm: Whether to normalize the density to the max of each category
                 ('single'), or the max of all categories ('all').
    :param mean: Color for lines showing the mean of each distribution.
    :param median: Color for lines showing the median of each distribution.
    :param ax: Optional matplotlib Axes instance to plot on.
    """
    ax: Axes = ax or new_axes()
    axf = AxesFormatter(ax)
    # get categories
    if categories is None:
        categories = data[x].unique()
    num_cats = len(categories)
    # colors
    if not isinstance(colors, list):
        colors = [colors] * num_cats
    # filter to category data
    data = data.loc[data[x].isin(categories)]
    # find max and min values for scaling
    y_min = data[y].min()
    y_max = data[y].max()
    # get counts for histogram
    z = data.groupby([x, y]).size()
    z_max = z.max()
    # plot densities
    for c, category, color in zip(
        range(1, num_cats + 1),
        categories,
        colors
    ):
        cat_hist = z.loc[category, :]
        if norm == 'all':
            z_max_cat = z_max
        elif norm == 'single':
            z_max_cat = cat_hist.max()
        else:
            raise ValueError('norm must be in {"all", "single"}')
        for (_, y_i), z_i in cat_hist.items():
            axf.add_rectangle(
                width=0.8, height=1,
                x_center=c, y_center=y_i,
                alpha=z_i / z_max_cat,
                color=color
            )
        if mean is not None:
            cat_mean = data.loc[data[x] == category, y].mean()
            axf.add_line(x=[c - 0.4, c + 0.4],
                         y=[cat_mean, cat_mean],
                         color=mean)
        if median is not None:
            cat_median = data.loc[data[x] == category, y].median()
            axf.add_line(x=[c - 0.4, c + 0.4],
                         y=[cat_median, cat_median],
                         color=median)
    # format axes
    axf.set_x_min(0.5)
    axf.set_x_max(len(categories) + 0.5)
    axf.set_y_min(y_min - 1)
    axf.set_y_max(y_max + 1)
    axf.x_ticks.set_locations(list(range(1, 1 + len(categories))))
    axf.x_ticks.set_labels(categories)
    axf.set_text(x_label=x, y_label=y)

    return ax


def categorical_continuous_values_histogram(
        data: DataFrame,
        x: str, y: str,
        log_y: bool = False,
        bins: int = 100,
        q_lim: Optional[Tuple[float, float]] = None,
        categories: Optional[List[str]] = None,
        colors: Union[Color, List[Color]] = 'k',
        norm: str = 'single',
        mean: Optional[Color] = None,
        median: Optional[Color] = None,
        ax: Optional[Axes] = None
):
    """
    Plot a histogram of several categories together.

    :param data: DataFrame with columns x and y
    :param x: Name of the category column. Categories will be found from the
              unique values of this column.
    :param y: Name of the value column. Each value is assumed to be a count,
              and the number of each count value will be counted.
    :param log_y: Whether to take log10 of the data.
    :param bins: Number of equally-spaced bins to cut the data into.
    :param q_lim: Optional percentile range to filter to e.g. (0, 0.99).
    :param categories: Optional override for categories of x. Use to select a
                       subset of x, or to reorder x.
    :param colors: Single color or list of colors to override default color of
                   each histogram.
    :param norm: Whether to normalize the density to the max of each category
                 ('single'), or the max of all categories ('all').
    :param mean: Color for lines showing the mean of each distribution.
    :param median: Color for lines showing the median of each distribution.
    :param ax: Optional matplotlib Axes instance to plot on.
    """
    ax: Axes = ax or new_axes()
    axf = AxesFormatter(ax)
    # get categories
    if categories is None:
        categories = data[x].unique()
    num_cats = len(categories)
    # colors
    if not isinstance(colors, list):
        colors = [colors] * num_cats
    # filter to category data
    data = data.loc[data[x].isin(categories)]
    # filter non-positive values for log-transform
    if log_y:
        data = data.loc[data['y'] > 0]
    # find max and min values for scaling
    if log_y:
        y_log = data[y].map(log10)
        y_min = y_log.min()
        y_max = y_log.max()
    else:
        y_min = data[y].min()
        y_max = data[y].max()
    # get counts for histogram
    z = {}
    z_max_cats = {}
    # calculate counts and maxes
    for category in categories:
        cat_data = data.loc[data[x] == category, y]
        if log_y:
            cat_data = cat_data.map(log10)
        if q_lim is not None:
            q_low, q_high = cat_data.quantile([q_lim[0], q_lim[1]])
            cat_data = cat_data.loc[
                (cat_data >= q_low) & (cat_data <= q_high)
            ]
        z[category] = cut(cat_data, bins).value_counts().sort_index()
        z_max_cats[category] = z[category].max()
    z_max = max(z_max_cats.values())
    # plot densities
    for c, category, color in zip(
            range(1, num_cats + 1),
            categories,
            colors
    ):
        if norm == 'all':
            z_max_cat = z_max
        elif norm == 'single':
            z_max_cat = z_max_cats[category]
        else:
            raise ValueError('norm must be in {"all", "single"}')
        for rng, z_i in z[category].items():
            axf.add_rectangle(
                width=0.8, height=rng.length,
                x_center=c, y_center=rng.mid,
                alpha=z_i / z_max_cat,
                color=color
            )
        if mean is not None:
            cat_mean = data.loc[data[x] == category, y].mean()
            if log_y:
                cat_mean = log10(cat_mean)
            axf.add_line(x=[c - 0.4, c + 0.4],
                         y=[cat_mean, cat_mean],
                         color=mean)
        if median is not None:
            cat_median = data.loc[data[x] == category, y].median()
            if log_y:
                cat_median = log10(cat_median)
            axf.add_line(x=[c - 0.4, c + 0.4],
                         y=[cat_median, cat_median],
                         color=median)
    # format axes
    axf.set_x_min(0.5)
    axf.set_x_max(len(categories) + 0.5)
    axf.set_y_min(y_min - 1)
    axf.set_y_max(y_max + 1)
    axf.x_ticks.set_locations(list(range(1, 1 + len(categories))))
    axf.x_ticks.set_labels(categories)
    axf.set_text(x_label=x, y_label=y)

    return ax


def do_test_discrete_plot():

    from scipy.stats import poisson
    p = concatenate([
        poisson(3).rvs(1_000),
        poisson(7).rvs(1_000),
        poisson(10).rvs(1_000)
    ])
    d = DataFrame({
        'y': p,
        'x': ['a'] * 1000 + ['b'] * 1_000 + ['c'] * 1_000
    })
    ax = categorical_discrete_values_histogram(
        data=d, x='x', y='y'
    )
    plt.show()
    ax = categorical_discrete_values_histogram(
        data=d, x='x', y='y', categories=['c', 'a']
    )
    plt.show()
    ax = categorical_discrete_values_histogram(
        data=d, x='x', y='y', categories=['c', 'a'], colors=['r', 'g']
    )
    AxesFormatter(ax).set_axis_below().grid()
    ax = categorical_discrete_values_histogram(
        data=d, x='x', y='y', categories=['c', 'a'], colors=['r', 'g'],
        norm='all', mean='b', median='purple'
    )
    AxesFormatter(ax).set_axis_below().grid()
    plt.show()


def do_test_continuous_plot():

    from scipy.stats import norm
    n = concatenate([
        norm(5, 1).rvs(10_000),
        norm(7, 2).rvs(10_000),
        norm(10, 1).rvs(10_000)
    ])
    d = DataFrame({
        'y': n,
        'x': ['a'] * 10_000 + ['b'] * 10_000 + ['c'] * 10_000
    })
    ax = categorical_continuous_values_histogram(
        data=d, x='x', y='y',
        categories=['c', 'a', 'b'], colors=['b', 'r', 'g'],
        norm='all', mean='b', median='purple',
        log_y=False
    )
    plt.show()
    ax = categorical_continuous_values_histogram(
        data=d, x='x', y='y',
        categories=['c', 'a', 'b'], colors=['b', 'r', 'g'],
        norm='all', mean='b', median='purple',
        log_y=True
    )
    plt.show()
    ax = categorical_continuous_values_histogram(
        data=d, x='x', y='y',
        categories=['c', 'a', 'b'], colors=['b', 'r', 'g'],
        norm='all', mean='b', median='purple',
        log_y=False, q_lim=(0.1, 0.9)
    )
    plt.show()


if __name__ == '__main__':

    # do_test_discrete_plot()
    do_test_continuous_plot()
