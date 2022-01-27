# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_loading_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Loading(object):
    def setupUi(self, Loading):
        Loading.setObjectName("Loading")
        Loading.resize(501, 133)
        self.gridLayout = QtWidgets.QGridLayout(Loading)
        self.gridLayout.setObjectName("gridLayout")
        self.labelMessage1 = QtWidgets.QLabel(Loading)
        self.labelMessage1.setText("")
        self.labelMessage1.setObjectName("labelMessage1")
        self.gridLayout.addWidget(self.labelMessage1, 0, 0, 1, 1)
        self.labelMessage2 = QtWidgets.QLabel(Loading)
        self.labelMessage2.setText("")
        self.labelMessage2.setObjectName("labelMessage2")
        self.gridLayout.addWidget(self.labelMessage2, 1, 0, 1, 1)

        self.retranslateUi(Loading)
        QtCore.QMetaObject.connectSlotsByName(Loading)

    def retranslateUi(self, Loading):
        _translate = QtCore.QCoreApplication.translate
        Loading.setWindowTitle(_translate("Loading", "Dialog"))

