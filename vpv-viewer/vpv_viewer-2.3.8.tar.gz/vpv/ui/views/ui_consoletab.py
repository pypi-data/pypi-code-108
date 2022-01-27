# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_consoletab.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_console(object):
    def setupUi(self, console):
        console.setObjectName("console")
        console.resize(761, 737)
        self.verticalLayout = QtWidgets.QVBoxLayout(console)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.verticalLayout.addLayout(self.mainLayout)

        self.retranslateUi(console)
        QtCore.QMetaObject.connectSlotsByName(console)

    def retranslateUi(self, console):
        _translate = QtCore.QCoreApplication.translate
        console.setWindowTitle(_translate("console", "Form"))

from . import resources_rc
