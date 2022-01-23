#!/usr/bin/env python3

# graphic universal library

import os, sys

import matplotlib.pyplot as plt

# initialization of single plot
def start_plot(gw=15, gh=9):
    fig, ax = plt.subplots(figsize=(gw,gh))
    return fig, ax

# show save graph
#   show  1:show graph 0 don't show
#   fn - file name where to save the graph
def show_plot(show,fig,ax,x="x",y="y",t="title", fn=None, grid=True):
    handles, labels = ax.get_legend_handles_labels()  # count legends
    if labels: ax.legend()
    if grid: ax.grid()
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(t)
    if fn is not None:  fig.savefig(fn)
    if show: plt.show()
    plt.close()


def draw_plot(x,y):
    fig, ax = start_plot()
    ax.plot(x,y,label='xy')
    show_plot(1,fig,ax)

#-----------------------------------------------------------------------------------
# variant with a small graph below the main graph - eg. to show errors
# usage:
#     fig, ax1, ax2 = start_plot2()   - ax2=None - only one graph
#     ax1.plot(x, y, label="xy")
#     show_plot2(1, fig, ax1, ax2)
#     show_plot2(show,fig,ax1,ax2,x1="x",y1="y",t1="title",x2=None,y2=None,t2=None, fn=None)

def start_plot2(gw=15, gh=9, ratios=[5,1], ax2=True):
    if ax2 is None: # only one axis
        fig, ax1 = plt.subplots(figsize=(gw, gh))
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(gw, gh), gridspec_kw={'height_ratios': ratios})
    return fig, ax1, ax2

# for ax2=None is ax2 ignored, same usage as single show_plot()
# show 1:show graph 0 don't shown but save to file -1:do nothing just close plot
def show_plot2(show,fig,ax1,ax2,x1="x",y1="y",t1="title",x2=None,y2=None,t2=None, fn=None, grid1=True, grid2=True):
    if show not in (1,0,-1):
        print("Using bad show {}".format(show))
        exit(-1)
    if show == -1:
        plt.close()
        return
    handles, labels = ax1.get_legend_handles_labels()  # count legends
    if labels: ax1.legend()
    if grid1: ax1.grid()
    if ax2 is None or x2 is not None:  # label of x1 if x2 not used  or we need different labels of ax1 and ax2
        ax1.set_xlabel(x1)
    ax1.set_ylabel(y1)
    ax1.set_title(t1)

    if ax2 is not None:
        handles, labels = ax2.get_legend_handles_labels()  # count legends
        if labels: ax2.legend()
        if grid2: ax2.grid()
        if x2 is None:
            ax2.set_xlabel(x1)    # same label as ax1 if not set
        else:
            ax2.set_xlabel(x2)
        if y2 is not None:
            ax2.set_ylabel(y2)
        if t2 is not None:
            ax2.set_title(t2)

    if fn is not None:  fig.savefig(fn)
    if show==1: plt.show()
    plt.close()


