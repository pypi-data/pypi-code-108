################################################################################
#                                                                              #
#                          PLOTTING HELPERS & AXES                             #
#                                                                              #
################################################################################

import numpy as np
import matplotlib.pyplot as plt
import os, sys

from ..mpl.compostela import *

__all__ = ['axes_plot', 'axes_square', 'axes_plotpull']


def axes_plot():
  fig, (axplot) = plt.subplots(1, 1)
  axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
  #axplot.set_xticks(axplot.get_yticks()[1:-1])
  axplot.tick_params(which='major', length=8, width=1, direction='in',
                    bottom=True, top=True, left=True, right=True)
  axplot.tick_params(which='minor', length=6, width=1, direction='in',
                    bottom=True, top=True, left=True, right=True)
  return fig, axplot


def axes_square():
  fig, (axplot) = plt.subplots(1, 1)
  axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
  #axplot.set_xticks(axplot.get_yticks()[1:-1])
  axplot.tick_params(which='major', length=8, width=1, direction='in',
                    bottom=True, top=True, left=True, right=True)
  axplot.tick_params(which='minor', length=6, width=1, direction='in',
                    bottom=True, top=True, left=True, right=True)
  axplot.set_aspect(1)
  return fig, axplot


def axes_plotpull():
  fig, (axplot,axpull) = plt.subplots(2, 1,
                                      sharex=True,
                                      gridspec_kw = {'height_ratios':[10, 3],
                                                     'hspace': 0.0}
                                      )
  axpull.xaxis.set_major_locator(plt.MaxNLocator(8))
  axplot.yaxis.set_major_locator(plt.MaxNLocator(8))
  axpull.set_ylim(-7, 7)
  axpull.set_yticks([-5, 0, +5])
  # axpull.set_xticks(axpull.get_xticks()[1:-1])
  # axplot.set_yticks(axplot.get_yticks()[1:-1])
  axplot.tick_params(which='major', length=8, width=1, direction='in',
                    bottom=True, top=True, left=True, right=True)
  axplot.tick_params(which='minor', length=6, width=1, direction='in',
                    bottom=True, top=True, left=True, right=True)
  axpull.tick_params(which='major', length=8, width=1, direction='in',
                     bottom=True, top=True, left=True, right=True)
  axpull.tick_params(which='minor', length=6, width=1, direction='in',
                     bottom=True, top=True, left=True, right=True)
  return fig, axplot, axpull

