from mpl_toolkits.axes_grid.parasite_axes import SubplotHost
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
from dateutil import parser
import sys
from dorianUtils.utilsD import Utils
utils=Utils()

def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)

def plotmtpaxis(x,y,sc=0.2,rm=0.65,lm=1,xlab='xlab',ylabs=[],markers=[],figSize=[8,8]):
    '''plot multiple axis
    x is a list
    y are list of lists'''
    fig, host = plt.subplots()
    fig.subplots_adjust(right=rm)
    fig.set_size_inches(figSize[0],figSize[1])
    palette = plt.get_cmap('jet',len(y))
    tkw = dict(size=6, width=1.5)
    if not markers:
        markers = ['o' for k in range(len(y))]
    if not ylabs:
        ylabs = ['ylab ' + str(k) for k in range(len(y))]
    #===================== host =============================
    host.plot(x, y[0],color=palette(0), linestyle="--", marker=markers[0], label=ylabs[0])
    host.set_xlabel(xlab)
    host.set_ylabel(ylabs[0])
    host.yaxis.label.set_color(palette(0))
    host.tick_params(axis='x', **tkw)
    host.tick_params(axis='y', colors=palette(0), **tkw)
    host.spines["left"].set_color(palette(0))
    pars = []
    #============================= parasite axes =============================r
    for k in range(1,len(y)):
        # par[k] =
        par= host.twinx()
        par.spines["right"].set_position(("axes", 1+(k-1)*sc))
        make_patch_spines_invisible(par)
        par.spines["right"].set_visible(True)
        par.spines["right"].set_color(palette(k))
        par.plot(x, y[k], color=palette(k),linestyle="--",marker=markers[k], label=ylabs[k])
        par.set_ylabel(ylabs[k])
        par.yaxis.label.set_color(palette(k))
        par.tick_params(axis='y', colors=palette(k), **tkw)
        # pars[k]=par
        # del par
    return fig

class multiY():
    #credits: http://matplotlib.sourceforge.net/examples/pylab_examples/multiple_yaxis_with_spines.html
    def __init__(self, height, width, X, LY, Xlabel, LYlabel, linecolor,
    set_marker, set_linestyle, fontsize, set_markersize,
    set_linewidth, set_mfc, set_mew, set_mec):

        self.X = X

        fig = plt.figure(figsize=(height, width))

        self.host = SubplotHost(fig, 111)

        plt.rc("font", size=fontsize)

        self.host.set_xlabel(Xlabel)
        self.host.set_ylabel(LYlabel)
        p1, = self.host.plot(X, LY, color=linecolor, marker=set_marker, ls=set_linestyle, ms=set_markersize, lw=set_linewidth, mfc=set_mfc, mew=set_mew, mec=set_mec)

        fig.add_axes(self.host)

        self.host.axis["left"].label.set_color(p1.get_color())
        self.host.tick_params(axis='y', color=p1.get_color())

    def parasites(self, set_offset, PY, PYlabel, side, Plinecolor,
    Pset_marker, Pset_linestyle, Pset_markersize, Pset_linewidth, Pset_mfc, Pset_mew, Pset_mec):
        par = self.host.twinx()
        par.axis["right"].set_visible(False)
        offset = (set_offset, 0)
        new_axisline = par.get_grid_helper().new_fixed_axis

        par.axis["side"] = new_axisline(loc=side, axes=par, offset=offset)

        par.axis["side"].label.set_visible(True)
        par.axis["side"].set_label(PYlabel)

        p2, = par.plot(self.X, PY,color=Plinecolor, marker=Pset_marker, ls=Pset_linestyle, ms=Pset_markersize, lw=Pset_linewidth, mfc=Pset_mfc, mew=Pset_mew, mec=Pset_mec)

        par.axis["side"].label.set_color(p2.get_color())
        par.tick_params(axis='y', colors=p2.get_color())

def demo_multiY():
#data
    x = (1, 3, 4, 6, 8, 9, 12)
    y1 = (0, 1, 2, 2, 4, 3, 2)
    y2 = (0, 3, 2, 3, 6, 4, 5)
    y3 = (50, 40, 40, 30, 20, 22, 10)
    y4 = (0.2, 0.5, 0.6, 0.9, 2, 5, 2)
    y5 = (2, 0.5, 0.9, 9, 12, 15, 12)
    y6 = (200, 500, 900, 900, 120, 150, 120)

    #height, width, x-data, y-datam, X-label, Y-label, line color, markerstyle, linestyle,
    # fontsize, markersize, linewidth, marker face color, marker edge with, marker edgecolor
    aa = multiY(8, 8, x, y1, "X-label", "Y-label", "r", "o", "None", 16, 8, 2, "none", "1", "r")
    #offset, y-data, Y-label, side, color, marker edge with, marker edgecolor
    aa.parasites(0, y2, "Parasite2", "right", "g", ">", "--", 10, 1, "none", "1", "g")
    aa.parasites(-60, y3, "Parasite3", "left", "b", "<", "-", 10, 1, "none", "1", "b")
    # aa.parasites(50, y4, "Parasite4", "right", "m", "s", "-.", 10, 1, "none", "1", "m")
    # aa.parasites(-100, y5, "Parasite5", "left", "y", "d", "none", 10, 1, "none", "1", "y")
    # aa.parasites(100, y6, "Parasite6", "right", "k", "*", "--", 10, 1, "none", "1", "k")

    #adjust the plot
    plt.subplots_adjust(left=0.20, bottom=0.15, right=0.78, top=0.92, wspace=0.05, hspace=0)
    plt.show()

def multiYmpl(df,**kwargs):
    listNames = df.columns
    listY = [df[k] for k in listNames]
    fig = plotmtpaxis(df.index,listY,**kwargs,ylabs=list(listNames))
    return fig

def demo_multiYmpl():
    df = px.data.stocks()
    df.index=[parser.parse(k) for k in df.date]
    del df['date']
    fig = multiYmpl(df.iloc[::10,:],sc=0.1,rm=0.7,figSize=[16,13],xlab='time (s)')
    plt.show(block=False)

def plotMultiUnitSmallPower(fileNb=0,skip=5,folder =None ,**kwargs):
    if not folder :
        folder = '/home/dorian/sylfen/exploreSmallPower/dataExported/'
    lsfiles = utils.get_listFilesPkl(folder,'.txt')
    print(utils.listWithNbs(lsfiles))
    df = pd.read_csv(folder + lsfiles[fileNb],index_col = 0,parse_dates=True)
    fig = multiYmpl(df.iloc[::skip,:],xlab='time',**kwargs)
    plt.show(block=False)
