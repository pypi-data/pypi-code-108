#!/usr/bin/env python3
#
# Author: Yipeng Sun
# License: BSD 2-clause
# Last Change: Thu Dec 16, 2021 at 04:57 PM +0100

import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt

from functools import wraps
from inspect import getfullargspec


###################
# General helpers #
###################

def filter_kwargs_func(kwargs, func):
    kw_func = getfullargspec(func).args

    kw_known = {k: kwargs[k] for k in kw_func if k in kwargs}
    kw_rest = {k: kwargs[k] for k in kwargs if k not in kw_known}

    return kw_known, kw_rest


def decorate_output(f, tight_layout=True, pad=0.):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        output = result[0]
        data = result[1:]

        if not output:
            return data

        fig = data[0]
        if tight_layout:
            plt.tight_layout(pad=pad)
        fig.savefig(output)
        fig.clf()
        plt.close(fig)

    return wrapper


def decorate_ax_style(f, *args, **kwargs):
    @wraps(f)
    def wrapper(*args, **kwargs):
        kw_known, kw_rest = filter_kwargs_func(kwargs, f)

        result = f(*args, **kw_known)
        result.update(kw_rest)

        return result

    return wrapper


################
# Plot helpers #
################

def tick_formatter_short(x, p):
    X = str(x)
    if len(X) > 4:
        return '{:2g}'.format(x)
    return x


def plot_prepare(figure=None, axis=None, title=None,
                 xtick_formatter=None, ytick_formatter=None,
                 xlabel=None, ylabel=None,
                 xlim=None, ylim=None,
                 xscale='linear', yscale='linear',
                 show_legend=True,
                 legend_add_args={'numpoints': 1, 'loc': 'best'}):
    fig = plt.figure() if not figure else figure

    if not axis:
        ax = fig.add_subplot()
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
    else:
        ax = axis

    if title:
        ax.set_title(title)

    if xtick_formatter:
        ax.get_xaxis().set_major_formatter(
            mp.ticker.FuncFormatter(xtick_formatter)
        )
    if ytick_formatter:
        ax.get_yaxis().set_major_formatter(
            mp.ticker.FuncFormatter(ytick_formatter)
        )

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    if xlim:
        ax.set_xlim(xlim)
    if ylim:
        ax.set_ylim(ylim)

    if show_legend:
        legend = lambda: ax.legend(**legend_add_args)
    else:
        legend = lambda: True

    return fig, ax, legend


def get_ytick_position_in_ax_coordinate(ax, scale):
    y_min, y_max = ax.get_ylim()
    raw_ticks = ax.get_yticks(minor=False)

    if scale == 'linear':
        ticks = [(tick - y_min)/(y_max - y_min) for tick in raw_ticks]
    elif scale == 'log':
        crd = np.vstack((np.zeros_like(raw_ticks), raw_ticks)).T
        ticks = ax.transAxes.inverted().transform(
            ax.transData.transform(crd))[:, 1]
    else:
        raise ValueError('Unknown axis scale: {}'.format(scale))

    return y_min, y_max, ticks


def ensure_no_majortick_on_topmost(ax, scale, thresh=0.9, ratio=0.19,
                                   verbose=False):
    y_min, y_max, ticks = get_ytick_position_in_ax_coordinate(ax, scale)

    if verbose:
        print('y range is: {}, {}'.format(y_min, y_max))
        print('y major ticks are: {}'.format(','.join([str(i) for i in ticks])))

    max_majortick = ticks[-2] if ticks[-1] > 1 else ticks[-1]
    if verbose:
        print('Max y tick is at: {}'.format(max_majortick))

    if max_majortick >= thresh:
        rel_tick_gap = ticks[1] - ticks[0]
        abs_tick_gap = rel_tick_gap * (y_max-y_min)
        padding = ratio * abs_tick_gap

        ax.set_ylim((y_min, y_max+padding))
        if verbose:
            print('Added y pad. Now y max is: {}'.format(y_max+padding))


################
# Data helpers #
################

def convert_bins_to_central_pos(bins):
    return bins[:-1] + (np.diff(bins)/2)


######################
# Plot style helpers #
######################

@decorate_ax_style
def ax_add_args_histo(label, color='blue', edgecolor='none'):
    if not edgecolor:
        edgecolor = color

    return {
        'color': color,
        'edgecolor': 'none',
        'label': label
    }


@decorate_ax_style
def ax_add_args_errorbar(label, color, yerr=None, marker='o',
                         markeredgecolor='none', ls='none'):
    return {
        'label': label,
        'ls': ls,
        'color': color,
        'marker': marker,
        'markeredgecolor': markeredgecolor,
        'yerr': yerr
    }


@decorate_ax_style
def ax_add_args_step(label, color, where='post'):
    return {
        'label': label,
        'color': color,
        'where': where
    }


@decorate_ax_style
def ax_add_args_fill(color, alpha=0.5, linewidth=0., step='post'):
    return {
        'color': color,
        'alpha': alpha,
        'linewidth': linewidth,
        'step': step
    }


@decorate_ax_style
def ax_add_args_hlines(label, color, linestyles='solid'):
    return {
        'label': label,
        'colors': color,
        'linestyles': linestyles
    }


ax_add_args_vlines = ax_add_args_hlines


@decorate_ax_style
def ax_add_args_hist2d(bins=None, cmap='YlOrRd'):
    return {'bins': bins, 'cmap': cmap}


################
# Simple plots #
################

@decorate_output
def plot_histo(bins, histo, histo_add_args,
               output=None, xtick_formatter=tick_formatter_short,
               **kwargs):
    fig, ax, legend = plot_prepare(xtick_formatter=xtick_formatter, **kwargs)
    mid_bins = convert_bins_to_central_pos(bins)
    ax.bar(mid_bins, histo, width=np.diff(bins), **histo_add_args)

    legend()
    return output, fig, ax


@decorate_output
def plot_errorbar(x, y, errorbar_add_args,
                  output=None, convert_x=True,
                  **kwargs):
    if convert_x:
        x = convert_bins_to_central_pos(x)

    fig, ax, legend = plot_prepare(**kwargs)
    ax.errorbar(x, y, **errorbar_add_args)

    legend()
    return output, fig, ax


@decorate_output
def plot_step(x, y, step_add_args,
              output=None,
              **kwargs):
    y = np.append(y, y[-1])

    fig, ax, legend = plot_prepare(**kwargs)
    ax.step(x, y, **step_add_args)

    legend()
    return output, fig, ax


@decorate_output
def plot_fill(x, y_range, fill_add_args,
              output=None,
              **kwargs):
    ymin, ymax = y_range
    ymin = np.append(ymin, ymin[-1])
    ymax = np.append(ymax, ymax[-1])

    fig, ax, legend = plot_prepare(**kwargs)
    ax.fill_between(x, ymin, ymax, **fill_add_args)

    legend()
    return output, fig, ax


@decorate_output
def plot_hlines(x, y, hlines_add_args,
                output=None,
                **kwargs):
    xmin = x[:-1]
    xmax = x[1:]

    fig, ax, legend = plot_prepare(**kwargs)
    ax.hlines(y, xmin, xmax, **hlines_add_args)

    legend()
    return output, fig, ax


@decorate_output
def plot_vlines(x, y, vlines_add_args,
                output=None, convert_x=True,
                **kwargs):
    if convert_x:
        x = convert_bins_to_central_pos(x)

    ymin = y[0]
    ymax = y[1]

    fig, ax, legend = plot_prepare(**kwargs)
    ax.vlines(x, ymin, ymax, **vlines_add_args)

    legend()
    return output, fig, ax


############
# 2D plots #
############

@decorate_output
def plot_hexbin(x, y, hexbin_add_args,
                output=None, colorbar_label=None,
                **kwargs):
    fig, ax, legend = plot_prepare(**kwargs)
    color_mesh = ax.hexbin(x, y,  **hexbin_add_args)
    cb = fig.colorbar(color_mesh, ax=ax)

    if colorbar_label:
        cb.set_label(colorbar_label)

    legend()
    return output, fig, ax


@decorate_output
def plot_hist2d(x, y, hist2d_add_args,
                output=None, colorbar_label=None,
                **kwargs):
    fig, ax, legend = plot_prepare(**kwargs)
    _, _, _, color_mesh = ax.hist2d(x, y, **hist2d_add_args)
    cb = fig.colorbar(color_mesh, ax=ax)

    if colorbar_label:
        cb.set_label(colorbar_label)

    legend()
    return output, fig, ax


###################
# Composite plots #
###################

@decorate_output
def plot_top(top_plotters,
             output=None,
             legend_add_args={'numpoints': 1, 'loc': 'best'},
             **kwargs):
    fig, ax, _ = plot_prepare(**kwargs)

    for p in top_plotters:
        p(fig, ax)

    ax.legend(**legend_add_args)
    return output, fig, ax


def plot_top_bot(top_plotters, bot_plotters,
                 title=None,
                 xlabel=None, ax1_ylabel=None, ax2_ylabel=None,
                 ax1_yscale='linear', ax2_yscale='linear',
                 height_ratios=[3, 1],
                 legend_add_args={'numpoints': 1, 'loc': 'best'},
                 **kwargs):
    fig = plt.figure()
    fig.set_tight_layout({'pad': 0.})

    spec = fig.add_gridspec(ncols=1, nrows=2, height_ratios=height_ratios)
    spec.update(hspace=0.)

    ax1 = fig.add_subplot(spec[0, 0])
    ax1.set_yscale(ax1_yscale)

    if ax1_ylabel:
        ax1.set_ylabel(ax1_ylabel)
    if title:
        ax1.set_title(title)

    ax2 = fig.add_subplot(spec[1, 0], sharex=ax1)
    ax2.set_yscale(ax2_yscale)

    if xlabel:
        ax2.set_xlabel(xlabel)
    if ax2_ylabel:
        ax2.set_ylabel(ax2_ylabel)

    for p in top_plotters:
        p(fig, ax1, **kwargs)

    for p in bot_plotters:
        p(fig, ax2, **kwargs)

    # Always show legend for top
    ax1.legend(**legend_add_args)

    # Remove the horizontal labels for the top plot
    for tick in ax1.xaxis.get_major_ticks():
        tick.label1.set_visible(False)

    # No offset (like +1 on top of the axis)
    if ax2_yscale == 'linear':
        ax2.ticklabel_format(axis='y', useOffset=False)

    # Add some padding if the TOPMOST ylabel of bot is too close to the top
    ensure_no_majortick_on_topmost(ax2, ax2_yscale)

    # Align y labels
    fig.align_ylabels()

    return fig, ax1, ax2
