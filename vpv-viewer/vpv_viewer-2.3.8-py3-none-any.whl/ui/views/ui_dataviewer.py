# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_dataviewer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_DataViewer(object):
    def setupUi(self, DataViewer):
        DataViewer.setObjectName("DataViewer")
        DataViewer.resize(430, 282)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayoutInfo = QtWidgets.QGridLayout()
        self.gridLayoutInfo.setObjectName("gridLayoutInfo")
        self.verticalLayout.addLayout(self.gridLayoutInfo)
        self.plotWidget = PlotWidget(self.dockWidgetContents)
        self.plotWidget.setObjectName("plotWidget")
        self.verticalLayout.addWidget(self.plotWidget)
        DataViewer.setWidget(self.dockWidgetContents)

        self.retranslateUi(DataViewer)
        QtCore.QMetaObject.connectSlotsByName(DataViewer)

    def retranslateUi(self, DataViewer):
        _translate = QtCore.QCoreApplication.translate
        DataViewer.setWindowTitle(_translate("DataViewer", "DockWidget"))

from pyqtgraph import PlotWidget
