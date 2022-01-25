import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.legend import Legend
import numpy as np
from functools import wraps

def plot_to_ax(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if kwargs.get('ax', None) is not None:
            show_here = False
        else:
            _, kwargs['ax'] = plt.subplots()
            show_here = True

        result = func(*args, **kwargs)
        if kwargs.get('grid', False) is True:
            kwargs['ax'].grid(True)

        if show_here:
            plt.show()

        return result

    return wrapper


def return_fig(func):
    return_fig_key = 'return_fig'

    @wraps(func)
    def wrapper(*args, **kwargs):
        cond = kwargs.get(return_fig_key, False)
        if cond:
            kwargs.pop(return_fig_key)

        fig: plt.Figure = func(*args, **kwargs)

        if cond:
            return fig
        else:
            fig.show()

    return wrapper


def get_subplots_iter(i, j, **kwargs):
    if i == 1 and j == 1:
        return plt.figure(), plt.gca()

    fig, ax_list = plt.subplots(i, j, **kwargs)
    for ax in ax_list.flatten():
        ax.grid()
    ax_iter = iter(ax_list.flatten())

    return fig, ax_iter


def get_n_predetermined_colors(n, opacity_hex_str="FF", color_set=0):
    set0 = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF', '#FF8800', '#22FFAA', '#8844FF',
            '#00851b', '#f96c6c', '#b856a1', '#130995']
    set1 = ['#AA0000', '#00AA00', '#0000AA', '#AAAA00', '#AA00AA', '#00AAAA', '#AA5500', '#22AA77', '#5544AA',
            '#247334', '#e33232', '#80366e', '#262075']
    if color_set == 0:
        color_list = set0 + set1
    elif color_set == 1:
        color_list = set1 + set0
    else:
        raise ValueError('color set is not defined')

    color_list = [color + opacity_hex_str for color in color_list]

    n_in_set = len(color_list)
    if n > n_in_set:
        color_list += list(get_n_predetermined_colors(
            n - n_in_set, opacity_hex_str=opacity_hex_str, color_set=color_set
        ))
    return np.array(color_list[:n])


def get_random_colors(size, opacity_hex_str="FF", diff_thresh=150):
    color_list = list()
    last_color = None
    for _ in range(size):
        while True:
            new_color = np.random.randint(16, 256, size=3)
            if last_color is not None:
                color_diff = sum(new_color - last_color)
                if np.abs(color_diff) > diff_thresh:
                    last_color = new_color
                    break
            else:
                last_color = new_color
                break
        color_hex_list = [hex(x).replace('0x', '') for x in new_color]
        new_color_hex = '#' + ''.join(color_hex_list + [opacity_hex_str])
        color_list.append(new_color_hex)

    return np.array(color_list)


def add_legend(ax, labels, colors, **kwargs):
    handles = [mpatches.Patch(color=color, label=label)
               for color, label in zip(colors, labels)]
    legend = Legend(parent=ax, handles=handles, labels=labels, **kwargs)
    legend.set_draggable(True)
    ax.add_artist(legend)


@plot_to_ax
def plot_markers(leads_dict, markers_dict, bounds=None, ax=None):
    assert type(markers_dict) == dict

    # plot markers
    if bounds is None:
        start, stop = (-float('inf'), float('inf'))
    else:
        start, stop = bounds

    colors = get_n_predetermined_colors(len(markers_dict), opacity_hex_str='FF')

    # slice leads
    for lead_name, lead_list in leads_dict.items():
        lead_array = np.array(lead_list)
        mask = np.logical_and(start < lead_array, lead_array < stop)
        leads_dict[lead_name] = lead_array[mask]

    # slice markers
    for marker_name, marker_list in markers_dict.items():
        marker_array = np.array(marker_list)
        mask = np.logical_and(start < marker_array, marker_array < stop)
        leads_dict[marker_name] = marker_array[mask]

    # TODO FINISH AND USE IN QRS/MEANS plotters

    # legend
    labels = list(markers_dict.keys())
    handles = [mpatches.Patch(color=color, label=label)
               for color, label in zip(colors, labels)]
    legend = Legend(parent=ax, handles=handles, labels=labels)
    legend.set_draggable(True)
    ax.add_artist(legend)


@plot_to_ax
def plot_with_colors(x, y, colors, labels=None, ax=None):
    length_list = [len(val) for val in [x, y, colors]]
    if not all([length_list[0] == val for val in length_list]):
        raise ValueError(f'x, y and colors should be the same size but has lengths {length_list}')

    color_unique = np.unique(colors)
    if not (len(color_unique) == len(labels)):
        raise ValueError('len(np.unique(colors)) != len(labels)')

    for color in color_unique:
        mask = colors == color
        ax.scatter(x[mask], y[mask], color=color, marker='*')

    if labels is not None:
        handles = [mpatches.Patch(color=color, label=label)
                   for color, label in zip(color_unique, labels)]

        legend = Legend(parent=ax, handles=handles, labels=labels)
        legend.set_draggable(True)
        ax.add_artist(legend)