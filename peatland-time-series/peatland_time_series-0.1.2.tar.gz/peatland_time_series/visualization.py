from typing import Optional, Set, Tuple

import matplotlib.pyplot as plt
import numpy
import pandas

TWIN_COLOR = 'royalblue'


def show_selector(sy: pandas.DataFrame, figsize: Optional[Tuple[int, int]] = None, *args, **kwargs) -> Set[int]:
    """Plot the Depth in function of Sy and allow the selection of data.

    This function plot the Depth(Sy) relation and allows the selection of
    data points. It allows the user to easily retrieve aberrant points
    without too much hassle. The selected data points will appear in
    red when clicked.
    
    Examples
    --------
    >>> selected_indexes = show_selector(sy)
    >>> print(selected_indexes)
     {0, 100, 5, 101, 103, 46, 79, 47, 19, 24}

    Parameters
    ----------
    sy
        The Sy DataFrame (same format as the `calculate_sy` output).
    figsize
        Optional, a tuple (width, height).
    args
        Optional, arguments that will be given to the scatter plot.
    kwargs
        Optional, named arguments that will be given to the scatter plot.

    Returns
    -------
    Set[int]
        A set of indexes of the selected data points.
    """
    if figsize:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig, ax = plt.subplots()

    scatter_plot = ax.scatter(sy['sy'], sy['depth'], picker=True, color=['blue'] * len(sy['sy']), *args, **kwargs)
    ax.set_xlabel('Sy')
    ax.set_ylabel('Depth [m]')

    selected_indexes = set()

    def on_pick(event):
        indexes = event.ind
        for index in indexes:
            selected_indexes.add(index)
            scatter_plot._facecolors[index] = numpy.array([1, 0, 0, 1])  # Set to color Red
            scatter_plot._edgecolors[index] = numpy.array([1, 0, 0, 1])  # Set to color Red
            fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', on_pick)
    plt.show()

    return selected_indexes


def plot_depth(sy: pandas.DataFrame, *args, **kwargs) -> None:
    """Plot the depth in function of Sy.
    
    Examples
    --------
    ```python
        time_series = read_time_series('tests/data/time_series/time_series/ahlenmoor/ahlenmoor_af_siteam5.csv')
    sy1 = calculate_sy(time_series=time_series)

    time_series2 = read_time_series('tests/data/time_series/time_series/ahlenmoor/ahlenmoor_af_siteam4.csv')
    sy2 = calculate_sy(time_series=time_series2)

    sy1 = filter_sy(sy1, sy_min=0, delta_h_min=.01, precipitation_sum_min=10, precipitation_sum_max=100)
    sy2 = filter_sy(sy2, sy_min=0, delta_h_min=.01, precipitation_sum_min=10, precipitation_sum_max=100)

    visualization.plot_depth(sy1, label='Sy 1', color='blue')
    visualization.plot_depth(sy2, label='Sy 2', color='red')
    plt.legend()

    plt.show()
    ```

    Parameters
    ----------
    sy
        DataFrame of Sy, obtained by the `calculate_sy` function.
    args
        Any args that will be give to to the plt.scatter plot.
    kwargs
        Any named args that will be give to to the plt.scatter plot.

    Returns
    -------
    None
    """
    plt.scatter(
        x=sy['sy'],
        y=sy['depth'],
        *args,
        **kwargs
    )
    plt.xlabel('Sy')
    plt.ylabel('Depth [m]')


def show_water_level(
        time_series: pandas.DataFrame,
        sy: pandas.DataFrame,
        event_index: int,
        time_before: pandas.Timedelta,
        time_after: pandas.Timedelta,
        fig_size: Optional[Tuple[int, int]] = None,
        date_format: Optional[str] = '%H',
        xlabel_rotation: Optional[int] = 0) -> None:
    """Plot the water level in function of the time.

    Examples
    --------
    ```python
    time_series = read_time_series('tests/data/time_series/time_series/ahlenmoor/ahlenmoor_af_siteam5.csv')
    sy = calculate_sy(time_series)

    show_water_level(
        time_series,
        sy,
        event_index=30,
        time_before=pandas.Timedelta(hours=10),
        time_after=pandas.Timedelta(hours=20)
    )
    ```

    Parameters
    ----------
    time_series
        Time series as a DataFrame (from `read_time_series`).
    sy
        Sy as a DataFrame (from `calculate_sy`).
    event_index
        Index of the event in Sy.
    time_before
        pandas.Timedelta before the chosen event.
    time_after
        pandas.Timedelta after the chosen event.
    date_format
        Date format (see https://strftime.org/).
    fig_size
        (width, height), fig size given to plt.subplots.
    xlabel_rotation
        Rotation of the x axis label. This may be useful when using complete dates on the x axis.

    Returns
    -------
    None
    """
    beginning = sy['date_beginning'].iloc[event_index] - time_before
    ending = sy['date_ending'].iloc[event_index] + time_after

    sub_time_series = time_series.loc[beginning:ending]

    fig, ax = plt.subplots(figsize=fig_size if fig_size else (10, 6))

    # Water table Depth plot
    ax.plot(sub_time_series.index, sub_time_series['data_wtd'], color='black')
    ax.set_xlabel('Time [h]')
    ax.set_ylabel('Water level [m]')


    # Twin plot for the precipitation
    # ------------------------------------------
    ax_precipitation = ax.twinx()
    ax_precipitation.bar(
        sub_time_series.index,
        sub_time_series['data_prec'],
        color=TWIN_COLOR,
        alpha=0.5,
        width=0.02
    )
    # Setting the color to all elements of the twin plot
    ax_precipitation.set_ylabel('Prec. [mm]', color=TWIN_COLOR)
    ax_precipitation.spines['right'].set_color(TWIN_COLOR)
    ax_precipitation.tick_params(axis='y', colors=TWIN_COLOR)

    # Setting the values for the x axis
    time_values = sub_time_series.index.map(lambda x: x.strftime(date_format))
    ax.set_xticks(sub_time_series.index, time_values, rotation=xlabel_rotation)

    ax.scatter(
        x=sy['idx_max'].iloc[[event_index]],
        y=sy['max_wtd'].iloc[[event_index]],
        s=100
    )
    ax.scatter(
        x=sy['idx_min'].iloc[[event_index]],
        y=sy['min_wtd'].iloc[[event_index]],
        s=100
    )

    plt.tight_layout()
    plt.show()
