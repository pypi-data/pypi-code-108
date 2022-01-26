__author__ = 'labx'

import sys

try:
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib import figure as matfig
    import pylab
except ImportError:
    print(sys.exc_info()[1])
    pass

from LibWiser.ToolLib import CommonPlots as LibWiserPlot

class WiserPlot:

    @classmethod
    def plot_histo(cls, plot_window, x, y, title, xtitle, ytitle):
        matplotlib.rcParams['axes.formatter.useoffset']='False'

        plot_window.addCurve(x, y, title, symbol='', color='blue', replace=True) #'+', '^', ','
        if not xtitle is None: plot_window.setGraphXLabel(xtitle)
        if not ytitle is None: plot_window.setGraphYLabel(ytitle)
        if not title is None: plot_window.setGraphTitle(title)
        plot_window.setInteractiveMode(mode='zoom')
        plot_window.resetZoom()
        plot_window.replot()

    def IntensityAtOE(self, **kwargs):
        return LibWiserPlot.IntensityAtOpticalElement(self, **kwargs)

    ### TODO: put other plots here as well, or just overwrite WiserPlot with CommonPlots as WiserPlot


from PyQt5 import QtWidgets

###############################################################
#
# MESSAGING
#
###############################################################

def showConfirmMessage(message, informative_text, parent=None):
    msgBox = QtWidgets.QMessageBox()
    if not parent is None: msgBox.setParent(parent)
    msgBox.setIcon(QtWidgets.QMessageBox.Question)
    msgBox.setText(message)
    msgBox.setInformativeText(informative_text)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    msgBox.setDefaultButton(QtWidgets.QMessageBox.No)

    return msgBox.exec_() == QtWidgets.QMessageBox.Yes

def showWarningMessage(message, parent=None):
    msgBox = QtWidgets.QMessageBox()
    if not parent is None: msgBox.setParent(parent)
    msgBox.setIcon(QtWidgets.QMessageBox.Warning)
    msgBox.setText(message)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msgBox.exec_()

def showCriticalMessage(message, parent=None):
    msgBox = QtWidgets.QMessageBox()
    if not parent is None: msgBox.setParent(parent)
    msgBox.setIcon(QtWidgets.QMessageBox.Critical)
    msgBox.setText(message)
    msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msgBox.exec_()
