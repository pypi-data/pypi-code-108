# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_manager.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ManageViews(object):
    def setupUi(self, ManageViews):
        ManageViews.setObjectName("ManageViews")
        ManageViews.resize(758, 834)
        ManageViews.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout_6.addWidget(self.tabWidget)
        ManageViews.setWidget(self.dockWidgetContents)

        self.retranslateUi(ManageViews)
        QtCore.QMetaObject.connectSlotsByName(ManageViews)

    def retranslateUi(self, ManageViews):
        _translate = QtCore.QCoreApplication.translate
        ManageViews.setWindowTitle(_translate("ManageViews", "Data manager"))

