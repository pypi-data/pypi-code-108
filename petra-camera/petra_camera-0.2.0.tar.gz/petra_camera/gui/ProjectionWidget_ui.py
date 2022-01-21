# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/ProjectionWidget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProjectionWidget(object):
    def setupUi(self, ProjectionWidget):
        ProjectionWidget.setObjectName("ProjectionWidget")
        ProjectionWidget.resize(849, 123)
        self.verticalLayout = QtWidgets.QVBoxLayout(ProjectionWidget)
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = GraphicsView(ProjectionWidget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)

        self.retranslateUi(ProjectionWidget)
        QtCore.QMetaObject.connectSlotsByName(ProjectionWidget)

    def retranslateUi(self, ProjectionWidget):
        _translate = QtCore.QCoreApplication.translate
        ProjectionWidget.setWindowTitle(_translate("ProjectionWidget", "Form"))

from pyqtgraph import GraphicsView
